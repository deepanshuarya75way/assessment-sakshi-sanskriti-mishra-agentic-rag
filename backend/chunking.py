from langchain_text_splitters import RecursiveCharacterTextSplitter
from load_docs import all_docs


splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)


chunks = splitter.split_documents(
    all_docs
)


print("\n")
print("="*50)

print(
    "Total Chunks:",
    len(chunks)
)

print("="*50)

print("\nSample Chunk:\n")

print(
    chunks[0].page_content
)

print("\n")

print(
    "Chunk length:",
    len(
        chunks[0].page_content
    )
)