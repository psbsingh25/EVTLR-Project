"""Source package with auto-loading skills support.

This package automatically discovers and registers skills from the skills/
directory when imported. Skills are loaded from YAML manifests in
skills/manifests/ and written to skills/registry.json for runtime access.

The loader runs automatically on package import to ensure skills are always
available before any agent operations begin.
"""

# Auto-run skills loader on package import
from .skills_loader import discover_and_register_skills

# Discover and register all skills
_registry = discover_and_register_skills()

# Expose key functions for manual skill access
from .skills_loader import get_skills_by_category, load_skill

__all__ = [
    "get_skills_by_category",
    "load_skill",
    "discover_and_register_skills",
]
