"""Simple skills loader that discovers manifests under `skills/manifests`.

On import, call `discover_and_register_skills()` to populate
`skills/registry.json` with discovered skills so runtime can prefer them.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "skills" / "manifests"
REGISTRY_FILE = ROOT / "skills" / "registry.json"

def discover_manifests():
    if not MANIFEST_DIR.exists():
        return []
    return sorted(MANIFEST_DIR.glob("*.yaml"))

def register(manifest_paths):
    registry = []
    for p in manifest_paths:
        try:
            import yaml
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
            registry.append(data)
        except Exception:
            continue
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry

def discover_and_register_skills():
    manifests = discover_manifests()
    return register(manifests)

if __name__ == "__main__":
    r = discover_and_register_skills()
    print(f"Registered {len(r)} skills")
