from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from chunking import chunks

client = QdrantClient(":memory:")

client.create_collection(
    collection_name="research_docs",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Extract and embed documents (filter out citations/references)
print("Creating embeddings and storing in Qdrant...")
points = []
skipped = 0

def is_likely_citation(text):
    """Filter out citation and reference sections"""
    # Skip if too short
    if len(text.strip()) < 50:
        return True
    
    # Skip if looks like a reference/citation
    citation_indicators = [
        text.count("pages ") > 2,
        text.count("et al.") > 0 and text.count("Proceedings") > 0,  # Only if BOTH present
        text.count("Proceedings of") > 1,  # Multiple proceedings
        len([word for word in text.split() if word.isupper()]) > len(text.split()) * 0.4,  # Too many acronyms
    ]
    
    # Don't filter company policy or similar business docs
    if any(keyword in text.lower() for keyword in ["policy", "leave", "benefit", "employee", "company"]):
        return False
    
    return any(citation_indicators)

for idx, chunk in enumerate(chunks):
    text = chunk.page_content
    
    # Skip citation chunks
    if is_likely_citation(text):
        skipped += 1
        continue
    
    embedding = model.encode(text)
    
    points.append(
        PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={"text": text, "source": chunk.metadata.get("source", "unknown")}
        )
    )

# Upload to Qdrant
if points:
    client.upsert(
        collection_name="research_docs",
        points=points
    )
    print(f"Stored {len(points)} embeddings in Qdrant (skipped {skipped} citation chunks)")
else:
    print("No chunks to store")

# Test query
def search_documents(query_text, top_k=3):
    from qdrant_client.models import Query
    query_embedding = model.encode(query_text)
    results = client.query_points(
        collection_name="research_docs",
        query=query_embedding.tolist(),
        limit=top_k
    )
    return results

# Test with a sample query
if points:
    print("\n" + "="*50)
    print("TESTING SEARCH:")
    print("="*50)
    test_query = "How many sick leaves are available?"
    results = search_documents(test_query)
    
    print(f"\nQuery: '{test_query}'")
    print(f"Found {len(results.points)} results:\n")
    
    for i, result in enumerate(results.points, 1):
        print(f"Result {i}:")
        print(f"  Score: {result.score:.4f}")
        print(f"  Text: {result.payload['text'][:100]}...")
        print(f"  Source: {result.payload['source']}")
        print()