from src.config import SAMPLE_DOCUMENTS_DIR, print_config_summary
from src.document_loader import load_documents_from_dir


def main() -> None:
    print_config_summary()

    documents = load_documents_from_dir(SAMPLE_DOCUMENTS_DIR)

    print("Loaded documents:", len(documents))

    for document in documents:
        print("Source:", document.source_path.name)
        print("Characters:", len(document.text))
        print("Preview:", document.text[:200])


if __name__ == "__main__":
    main()
