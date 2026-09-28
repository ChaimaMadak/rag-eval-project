from __future__ import annotations

import json
from pathlib import Path

import fitz


DATA_DIR = Path("data/raw")
PDF_DIR = DATA_DIR / "papers"
METADATA_PATH = DATA_DIR / "arxiv_metadata.json"
OUTPUT_PATH = DATA_DIR / "extracted_text.json"


def extract_pdf(pdf_path: Path) -> list[dict]:
    """Extract text from a PDF while preserving page boundaries."""

    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if not text:
                continue

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

    return pages


def main() -> None:
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        papers = json.load(f)

    documents = []

    for i, paper in enumerate(papers, start=1):
        paper_id = paper["id"].split("/")[-1]
        pdf_path = PDF_DIR / f"{paper_id}.pdf"

        if not pdf_path.exists():
            print(f"[{i}/{len(papers)}] Missing PDF: {paper_id}")
            continue

        print(f"[{i}/{len(papers)}] Extracting: {paper_id}")

        pages = extract_pdf(pdf_path)

        documents.append(
            {
                "paper_id": paper_id,
                "title": paper["title"],
                "authors": paper["authors"],
                "published": paper["published"],
                "pages": pages,
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            documents,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nExtracted {len(documents)} papers.")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()