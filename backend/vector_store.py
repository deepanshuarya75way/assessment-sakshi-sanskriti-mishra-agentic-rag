from functools import lru_cache
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from chunking import chunk_documents
from config import get_settings
from embeddings import get_embedding_model
from load_docs import load_documents


logger = logging.getLogger(__name__)
COLLECTION_NAME = "research_docs"
VECTOR_SIZE = 384


class VectorStore:
    def __init__(self):
        settings = get_settings()
        settings.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(settings.vector_store_path))
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if any(collection.name == COLLECTION_NAME for collection in collections):
            return

        documents, failures = load_documents()
        chunks = chunk_documents(documents)
        if not chunks:
            raise RuntimeError("The knowledge base contains no text chunks.")

        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        model = get_embedding_model()
        vectors = model.encode([chunk.page_content for chunk in chunks], show_progress_bar=False)
        points = [
            PointStruct(
                id=index,
                vector=vector.tolist(),
                payload={"text": chunk.page_content, "source": chunk.metadata.get("source", "unknown")},
            )
            for index, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        self.client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
        logger.info("Indexed %s document chunks", len(points))
        for failure in failures:
            logger.warning("Skipped document during indexing: %s", failure)

    def search(self, query: str, top_k: int = 3):
        vector = get_embedding_model().encode(query).tolist()
        result = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=top_k,
        )
        return result.points


@lru_cache(maxsize=1)
def get_vector_store():
    return VectorStore()


def search_documents(query: str, top_k: int = 3):
    try:
        return get_vector_store().search(query, top_k)
    except Exception as error:
        raise RuntimeError("Knowledge-base retrieval is unavailable. Check the documents and embedding model.") from error
