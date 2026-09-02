from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader

from config import PROJECT_ROOT


DOCUMENTS_DIR = PROJECT_ROOT / "data" / "research_papers"


def load_documents(documents_dir: Path = DOCUMENTS_DIR):
    """Load the repository's PDF and text knowledge-base files."""
    if not documents_dir.exists():
        raise FileNotFoundError(f"Knowledge-base directory does not exist: {documents_dir}")

    documents = []
    failures = []
    for path in sorted(documents_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".pdf", ".txt"}:
            continue
        try:
            loader = PyMuPDFLoader(str(path)) if path.suffix.lower() == ".pdf" else TextLoader(str(path), encoding="utf-8")
            documents.extend(loader.load())
        except Exception as error:
            failures.append(f"{path.name}: {error}")

    if not documents:
        detail = "; ".join(failures) if failures else "No supported documents were found."
        raise RuntimeError(f"Could not load knowledge-base documents. {detail}")

    return documents, failures
