from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader
)

import os
from pathlib import Path

all_docs = []

# Get the base directory (project root)
backend_dir = Path(__file__).parent
base_dir = backend_dir.parent

# Define paths
pdf_folder = str(base_dir / "data" / "research_papers")
txt_folder = str(base_dir / "data" / "research_papers" / "custom")


# -----------------------------
# Load PDFs
# -----------------------------

if os.path.exists(pdf_folder):
    for file in os.listdir(pdf_folder):

        if file.endswith(".pdf"):

            path = os.path.join(
                pdf_folder,
                file
            )

            print(f"Loading PDF: {file}")

            loader = PyMuPDFLoader(path)

            docs = loader.load()

        all_docs.extend(docs)
else:
    print(f"PDF folder not found: {pdf_folder}")


# -----------------------------
# Load TXT files
# -----------------------------

try:
    if os.path.exists(txt_folder):
        for file in os.listdir(txt_folder):
            if file.endswith(".txt"):
                path = os.path.join(txt_folder, file)
                print(f"Loading TXT: {file}")
                
                try:
                    # Try with encoding
                    loader = TextLoader(path, encoding="utf-8")
                    docs = loader.load()
                    all_docs.extend(docs)
                    print(f"  ✓ Loaded {len(docs)} docs from {file}")
                except Exception as e:
                    print(f"  ✗ Error loading {file}: {e}")
                    # Try with different encoding
                    try:
                        loader = TextLoader(path, encoding="latin-1")
                        docs = loader.load()
                        all_docs.extend(docs)
                        print(f"  ✓ Loaded {len(docs)} docs with latin-1 encoding")
                    except Exception as e2:
                        print(f"  ✗ Failed to load with latin-1: {e2}")
    else:
        print(f"Custom folder not found: {txt_folder}")

except FileNotFoundError:
    print(f"Error accessing TXT folder: {txt_folder}")


# -----------------------------
# Results
# -----------------------------

print("\n")
print("="*50)

print("Total loaded docs:", len(all_docs))

print("="*50)

print("\nSample content:\n")

print(
    all_docs[0].page_content[:500]
)