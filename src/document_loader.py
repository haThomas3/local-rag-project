from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class LoadedDocument:
    source_path: Path
    text: str


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def load_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    page_texts: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_texts.append(text.strip())

    return "\n\n".join(page_texts)


def load_document(path: Path) -> LoadedDocument:
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        text = load_text_file(path)
    elif suffix == ".pdf":
        text = load_pdf_file(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return LoadedDocument(source_path=path, text=text.strip())


def load_documents_from_dir(directory: Path) -> list[LoadedDocument]:
    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    documents: list[LoadedDocument] = []

    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            document = load_document(path)
            if document.text:
                documents.append(document)

    return documents
