"""Skills loader that discovers manifests under `skills/manifests`.

On import, call `discover_and_register_skills()` to populate
`skills/registry.json` with discovered skills so runtime can prefer them.

Auto-runs when this module is imported via `src/__init__.py`.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "skills" / "manifests"
REGISTRY_FILE = ROOT / "skills" / "registry.json"


def discover_manifests():
    """Discover all YAML manifest files in the manifests directory."""
    if not MANIFEST_DIR.exists():
        return []
    return sorted(MANIFEST_DIR.glob("*.yaml"))


def register(manifest_paths):
    """Register skills from manifest files into a structured registry.

    Returns structured registry with categories, skills list, and metadata.
    """
    skills_list = []
    categories = {}

    for p in manifest_paths:
        try:
            import yaml

            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            if data:
                skills_list.append(data)

                # Group by category
                category = data.get("category", "general")
                if category not in categories:
                    categories[category] = []
                categories[category].append(
                    {
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "version": data.get("version"),
                        "source": data.get("source"),
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to process {p}: {e}")
            continue

    # Create structured registry
    registry = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skills_count": len(skills_list),
        "categories": categories,
        "skills": skills_list,
    }

    # Write registry to file
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return registry


def discover_and_register_skills():
    """Discover all manifests and register them.

    Returns the structured registry dictionary.
    """
    manifests = discover_manifests()
    registry = register(manifests)
    return registry


def get_skills_by_category(category: str | None = None):
    """Get skills filtered by category.

    Args:
        category: Optional category filter ("data-download" or "eda")

    Returns:
        List of skills matching the category, or all skills if no category specified
    """
    if not REGISTRY_FILE.exists():
        return []

    try:
        registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        if category:
            return registry.get("categories", {}).get(category, [])
        return registry.get("skills", [])
    except Exception:
        return []


def load_skill(name: str):
    """Load a specific skill by name.

    Args:
        name: The skill name to load

    Returns:
        Skill manifest dict or None if not found
    """
    skills = get_skills_by_category()
    for skill in skills:
        if skill.get("name") == name:
            return skill
    return None


# Auto-run when module is loaded directly (not recommended for import)
# Use via src/__init__.py for proper auto-loading
if __name__ == "__main__":
    r = discover_and_register_skills()
    print(f"Registered {r['skills_count']} skills")
    print(f"Categories: {list(r['categories'].keys())}")
    for cat, skills in r["categories"].items():
        print(f"  - {cat}: {len(skills)} skills")
