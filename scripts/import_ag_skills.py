#!/usr/bin/env python3
"""Import ag-skills from skills-content branch into Agent Skills IO manifest format.

This script scans skills/vendor/ag-skills/ for skill directories containing SKILL.md files,
parses the YAML frontmatter, and generates Agent Skills IO-style YAML manifests under
skills/manifests/. It categorizes skills as 'data-download' or 'eda' based on their tags.

Usage:
    python scripts/import_ag_skills.py
"""

import re
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "skills" / "vendor" / "ag-skills"
MANIFEST_DIR = ROOT / "skills" / "manifests"

# Skills categorized by their primary purpose
DATA_DOWNLOAD_SKILLS = {
    "field-boundaries",
    "ssurgo-soil",
    "nasa-power-weather",
    "cdl-cropland",
    "sentinel2-imagery",
    "landsat-imagery",
    "interactive-web-map",
}

EDA_SKILLS = {
    "eda-explore",
    "eda-visualize",
    "eda-correlate",
    "eda-time-series",
    "eda-compare",
}


def parse_skill_md(skill_dir: Path) -> dict | None:
    """Parse YAML frontmatter from SKILL.md file."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None

    text = skill_md.read_text(encoding="utf-8")

    # Extract YAML frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        return frontmatter if isinstance(frontmatter, dict) else None
    except yaml.YAMLError:
        return None


def determine_category(skill_name: str, tags: list) -> str:
    """Determine skill category based on name and tags."""
    if skill_name in DATA_DOWNLOAD_SKILLS:
        return "data-download"
    elif skill_name in EDA_SKILLS:
        return "eda"

    # Fallback: infer from tags
    tag_set = set(tags) if tags else set()
    if tag_set & {
        "download",
        "usda",
        "nass",
        "sentinel-2",
        "landsat",
        "geospatial",
        "remote-sensing",
    }:
        return "data-download"
    elif tag_set & {"eda", "exploration", "pandas", "statistics", "analysis", "visualization"}:
        return "eda"

    return "general"


def create_manifest(skill_dir: Path, metadata: dict) -> dict:
    """Create Agent Skills IO format manifest from skill metadata."""
    skill_name = skill_dir.name

    # Handle different metadata formats
    name = metadata.get("name", skill_name)
    description = metadata.get("description", "")
    version = metadata.get("version", "1.0.0")
    author = metadata.get(
        "author",
        (
            metadata.get("metadata", {}).get("author", "Boreal Bytes")
            if isinstance(metadata.get("metadata"), dict)
            else "Boreal Bytes"
        ),
    )
    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    category = determine_category(skill_name, tags)

    manifest = {
        "name": name,
        "version": str(version),
        "author": author,
        "description": description,
        "license": "MIT",
        "source": f"skills/vendor/ag-skills/{skill_name}/",
        "entry": f"skills.vendor.ag-skills.{skill_name}",
        "category": category,
        "tags": tags,
        "imported_at": datetime.utcnow().isoformat() + "Z",
        "original_repo": "https://github.com/borealBytes/ag-skills/tree/skills-content",
    }

    return manifest


def main():
    """Main import function."""
    print("Starting ag-skills import from skills-content branch...")

    if not VENDOR.exists():
        print(f"Error: Vendor directory not found: {VENDOR}")
        return

    # Create manifests directory
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    imported_count = 0
    categories = {"data-download": 0, "eda": 0, "general": 0}

    # Find all skill directories
    for skill_dir in sorted(VENDOR.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("."):
            continue

        # Check if this is a skill directory (has SKILL.md)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        print(f"  Processing: {skill_dir.name}")

        # Parse SKILL.md frontmatter
        metadata = parse_skill_md(skill_dir)
        if not metadata:
            print(f"    Warning: Could not parse frontmatter for {skill_dir.name}")
            continue

        # Create manifest
        manifest = create_manifest(skill_dir, metadata)
        category = manifest["category"]
        categories[category] = categories.get(category, 0) + 1

        # Write manifest
        manifest_path = MANIFEST_DIR / f"{skill_dir.name}.yaml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"    Created: {manifest_path}")
        imported_count += 1

    print("\nImport complete!")
    print(f"  Total skills imported: {imported_count}")
    print("  Categories:")
    for cat, count in categories.items():
        if count > 0:
            print(f"    - {cat}: {count}")


if __name__ == "__main__":
    main()
