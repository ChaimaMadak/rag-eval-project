from __future__ import annotations

import json
import time
from pathlib import Path
import xml.etree.ElementTree as ET

import requests


ARXIV_API_URL = "https://export.arxiv.org/api/query"

HEADERS = {
    "User-Agent": "rag-eval-project/0.1 (contact: chaimamadak.1@gmail.com)",
    "Accept": "application/atom+xml",
}

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


def search_arxiv(
    query: str,
    max_results: int = 20,
    start: int = 0,
) -> list[dict]:
    """Search arXiv and return paper metadata."""

    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
    }

    response = requests.get(
        ARXIV_API_URL,
        params=params,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return parse_arxiv_response(response.text)


def parse_arxiv_response(xml_text: str) -> list[dict]:
    """Parse an arXiv Atom response into dictionaries."""

    root = ET.fromstring(xml_text)

    papers = []

    for entry in root.findall("atom:entry", ATOM_NS):
        paper_id = entry.findtext("atom:id", namespaces=ATOM_NS)
        title = entry.findtext("atom:title", namespaces=ATOM_NS)
        summary = entry.findtext("atom:summary", namespaces=ATOM_NS)
        published = entry.findtext("atom:published", namespaces=ATOM_NS)

        authors = [
            author.findtext("atom:name", namespaces=ATOM_NS)
            for author in entry.findall("atom:author", ATOM_NS)
        ]

        pdf_url = None

        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href")
                break

        papers.append(
            {
                "id": paper_id,
                "title": " ".join(title.split()) if title else None,
                "authors": authors,
                "abstract": " ".join(summary.split()) if summary else None,
                "published": published,
                "pdf_url": pdf_url,
            }
        )

    return papers


def save_metadata(papers: list[dict], output_path: str | Path) -> None:
    """Save paper metadata as JSON."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    papers = search_arxiv(
        query='all:"retrieval augmented generation"',
        max_results=5,
    )

    save_metadata(
        papers,
        "data/raw/arxiv_metadata.json",
    )

    print(f"Fetched {len(papers)} papers.")