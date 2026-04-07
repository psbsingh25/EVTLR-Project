#!/usr/bin/env python3
"""Embed dashboard image assets into a standalone HTML file.

Usage:
    python scripts/embed_dashboard_assets.py

Optional arguments:
    --html output/field_eda_dashboard.html
    --assets output/dashboard_assets
    --out output/field_eda_dashboard_embedded.html
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed dashboard assets as data URIs.")
    parser.add_argument(
        "--html",
        type=Path,
        default=Path("output/field_eda_dashboard.html"),
        help="Path to dashboard HTML file.",
    )
    parser.add_argument(
        "--assets",
        type=Path,
        default=Path("output/dashboard_assets"),
        help="Directory containing image assets referenced by the dashboard HTML.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("output/field_eda_dashboard_embedded.html"),
        help="Output path for standalone embedded dashboard HTML.",
    )
    return parser.parse_args()


def file_to_data_uri(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.name)
    if mime_type is None:
        mime_type = "application/octet-stream"
    b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


def embed_images(html: str, assets_dir: Path) -> tuple[str, int]:
    # Matches src='dashboard_assets/file.png' and src="dashboard_assets/file.png"
    pattern = re.compile(r"src=(['\"])dashboard_assets/([^'\"]+)\1")
    replaced_count = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal replaced_count
        quote = match.group(1)
        relative_file = match.group(2)
        image_path = assets_dir / relative_file
        if not image_path.exists():
            raise FileNotFoundError(f"Missing image asset: {image_path}")
        replaced_count += 1
        return f"src={quote}{file_to_data_uri(image_path)}{quote}"

    embedded_html = pattern.sub(replacer, html)
    return embedded_html, replaced_count


def main() -> None:
    args = parse_args()
    html_path = args.html
    assets_dir = args.assets
    output_path = args.out

    if not html_path.exists():
        raise FileNotFoundError(f"Dashboard HTML not found: {html_path}")
    if not assets_dir.exists():
        raise FileNotFoundError(f"Assets directory not found: {assets_dir}")

    html_text = html_path.read_text(encoding="utf-8")
    embedded_html, count = embed_images(html_text, assets_dir)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(embedded_html, encoding="utf-8")

    print(f"Embedded {count} image(s)")
    print(f"Wrote standalone dashboard: {output_path}")


if __name__ == "__main__":
    main()
