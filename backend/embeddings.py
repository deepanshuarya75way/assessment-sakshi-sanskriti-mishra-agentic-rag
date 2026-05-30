from sentence_transformers import SentenceTransformer
from chunking import chunks


print("Loading embedding model...")

model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)

print("Creating embeddings...")

texts = []

for chunk in chunks:
    texts.append(
        chunk.page_content
    )


embeddings = model.encode(
    texts
)


print("\n")
print("="*50)

print(
    "Total embeddings:",
    len(embeddings)
)

print(
    "Embedding dimension:",
    len(
        embeddings[0]
    )
)

print("="*50)