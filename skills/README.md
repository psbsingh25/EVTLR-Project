# Skills (vendor imports)

This directory contains vendor-imported agent skills. The current import source
is `borealBytes/ag-skills` (MIT). Files are vendored under `vendor/ag-skills`.

Use the import script to generate Agent Skills IO-style manifests:

```bash
python3 scripts/import_ag_skills.py
```

The loader `src/skills_loader.py` reads manifests under `skills/manifests/`
and writes `skills/registry.json` which runtime components can consult to
prefer imported skills.

Do not edit `vendor/ag-skills` contents directly; re-run the import process
when updating the vendor copy.
