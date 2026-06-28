import json

from src.chunker import chunk_documents
from src.config import SAMPLE_DOCUMENTS_DIR
from src.document_loader import load_documents_from_dir


def main() -> None:
    documents = load_documents_from_dir(SAMPLE_DOCUMENTS_DIR)
    chunks = chunk_documents(documents, chunk_size_words=40, overlap_words=10)

    print("Loaded documents:", len(documents))

    for document in documents:
        print("Document:", document.source_path.name)
        print("Characters:", len(document.text))

    print("Generated chunks:", len(chunks))

    for chunk in chunks[:5]:
        print(json.dumps(chunk.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
