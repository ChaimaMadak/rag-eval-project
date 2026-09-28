from __future__ import annotations

import json
import time
from pathlib import Path

import requests


HEADERS = {
    "User-Agent": "rag-eval-project/0.1 (contact: chaimamadak.1@gmail.com)",
}

DATA_DIR = Path("data/raw")
PDF_DIR = DATA_DIR / "papers"
METADATA_PATH = DATA_DIR / "arxiv_metadata.json"


def download_paper(
    pdf_url: str,
    output_path: Path,
) -> None:
    """Download a single PDF from arXiv."""

    response = requests.get(
        pdf_url,
        headers=HEADERS,
        timeout=60,
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/pdf" not in content_type:
        raise ValueError(
            f"Expected a PDF but received Content-Type: {content_type}"
        )

    output_path.write_bytes(response.content)


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    with METADATA_PATH.open("r", encoding="utf-8") as f:
        papers = json.load(f)

    for i, paper in enumerate(papers, start=1):
        paper_id = paper["id"].split("/")[-1]
        pdf_url = paper["pdf_url"]

        output_path = PDF_DIR / f"{paper_id}.pdf"

        if output_path.exists():
            print(f"[{i}/{len(papers)}] Already exists: {paper_id}")
            continue

        print(f"[{i}/{len(papers)}] Downloading: {paper_id}")

        try:
            download_paper(pdf_url, output_path)
        except (requests.RequestException, ValueError) as exc:
            print(f"  Failed: {exc}")
            continue

        # Avoid sending requests too quickly.
        time.sleep(3)


if __name__ == "__main__":
    main()