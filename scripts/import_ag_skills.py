#!/usr/bin/env python3
"""Import ag-skills package into Agent Skills IO manifest format.

This script scans `skills/vendor/ag-skills/src/ag_skills` for modules and
generates a simple Agent Skills IO-style YAML manifest per module under
`skills/manifests/`.

It is intentionally conservative: it does not execute vendor code. It only
inspects filenames and top-level docstrings to populate manifests.
"""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "skills" / "vendor" / "ag-skills"
SRC = VENDOR / "src" / "ag_skills"
MANIFEST_DIR = ROOT / "skills" / "manifests"


def extract_description(pyfile: Path) -> str:
    text = pyfile.read_text(encoding="utf-8")
    m = re.search(r'"""([\s\S]*?)"""', text)
    return (m.group(1).strip()) if m else ""


def main():
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    if not SRC.exists():
        print("No src/ag_skills package found in vendor copy.")
        return
    for p in sorted(SRC.glob("*.py")):
        if p.name in ("__init__.py", "__version__.py"):
            continue
        name = p.stem
        descr = extract_description(p)
        manifest = {
            "name": f"ag-skills.{name}",
            "source": str(p.relative_to(ROOT)),
            "license": "MIT",
            "description": descr or f"Imported from borealBytes/ag-skills: {name}",
            "entry": f"ag_skills.{name}",
        }
        out = MANIFEST_DIR / f"{name}.yaml"
        out.write_text(yaml.safe_dump(manifest), encoding="utf-8")
        print("Wrote", out)


if __name__ == "__main__":
    main()
