---
# PR-00000001: Import agent skills from borealBytes/ag-skills into repo

| Field               | Value |
| ------------------- | ----- |
| **PR**              | `#00000001` |
| **Author**          | Automated agent (assistant) |
| **Date**            | 2026-03-03 |
| **Status** | ✅ Ready for Review |
| **Branch**          | `skills-import` → `main` |
| **Related issues**  | N/A |
| **Deploy strategy** | Standard |

---

## 📋 Summary

### What changed and why

This PR (record) initiates the planned import of agent skills from the public repository `https://github.com/borealBytes/ag-skills/tree/main/skills-content` into this repository using the Agent Skills IO format (<https://agentskills.io/home>). The goal is to ensure these skills are available and always referenced by this repo when agent functionality is used.

### Impact classification

| Dimension         | Level             | Notes                                                                              |
| ----------------- | ----------------- | ---------------------------------------------------------------------------------- |
| **Risk**          | 🟡 Medium         | Repo integration work, but non-destructive initially (adds files and loaders).     |
| **Scope**         | Narrow → Moderate | Adds a `skills/` import area and loader logic; may touch bootstrapping code later. |
| **Reversibility** | Easily reversible | Can remove the `skills/` directory and loader changes.                             |
| **Security**      | Low               | We'll scan imported dependencies and check license.                                |

---

## 🔍 Changes (Planned)

### Change inventory

| File / Area                                    | Change type             | Description                                                                         |
| ---------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------- |
| `skills/`                                      | Added                   | Vendor/imported skills content from `borealBytes/ag-skills` (selected subset).      |
| `scripts/` or `src/`                           | Added/Modified (future) | Add a skills loader that checks for agent skills at runtime and prefers them first. |
| `docs/project/pr/pr-00000001-skills-import.md` | Added                   | This PR record (you are reading it).                                                |

### Architecture impact

We will add a small skill discovery/loader that runs early in agent bootstrapping. It will check `skills/` (and configured locations) for skills in Agent Skills IO format and register them so agent flows prefer these skills first.

---

## 🧪 Testing (Planned)

### How to verify

1. Checkout branch `skills-import`.
2. Run import script (TBD) that fetches and installs skills into `skills/`.
3. Run agent bootstrapping locally and confirm the loader discovers and registers at least one imported skill.

### Test coverage

Manual verification will be used initially; unit/integration tests will be added once the loader is implemented.

---

## 🔒 Security

### Security checklist

- [ ] No secrets or credentials introduced by import
- [ ] License compatibility verified (Apache-2.0 preferred)
- [ ] Dependencies scanned for known vulnerabilities

**Security impact:** Low — importing read-only skill content. We'll validate licenses before final import.

---

## ⚡ Breaking Changes

No breaking changes planned for this import. Initial work will add files and loader logic that is opt-in by configuration; later we will enable prefer-skill behavior and document the change.

---

## 🔄 Rollback Plan

Remove the `skills/` directory and revert loader changes. Use `git revert` for commits if needed.

---

## 🚀 Deployment

No external deployment required. The branch will be used for review and CI. After review and merge, agent bootstrap code will be updated to reference skills by default.

---

## ✅ Reviewer Checklist (Initial)

- [ ] Files follow project style/guides
- [ ] No secrets in imported content
- [ ] License checked and acceptable
- [ ] Skills loader behavior defined and documented

---

## ✅ Completed Implementation

All implementation tasks completed on 2026-03-04:

1. **✅ Audited skills-content branch** - Identified 12 agricultural data analysis skills
2. **✅ Vendor copy method selected** - Copied entire skills-content branch to `skills/vendor/ag-skills/`
3. **✅ Import script implemented** - Parses YAML frontmatter from SKILL.md files, generates Agent Skills IO manifests
4. **✅ Loader registration added** - Auto-runs on `import src` via `src/__init__.py`
5. **✅ All 12 skills verified** - Registry generated with structured categories

### Skills Imported by Category

**Data-download (7 skills):**

- cdl-cropland, field-boundaries, interactive-web-map, landsat-imagery, nasa-power-weather, sentinel2-imagery, ssurgo-soil

**EDA (5 skills):**

- eda-compare, eda-correlate, eda-explore, eda-time-series, eda-visualize

### Verification Results

```bash
$ python3 src/skills_loader.py
Registered 12 skills
Categories: ['data-download', 'eda']
  - data-download: 7 skills
  - eda: 5 skills

$ python3 -c "import src; print(f'Skills auto-loaded: {len(src._registry[\"skills\"])}')"
Skills auto-loaded: 12
```

---

## Next Steps (Post-Merge)

1. Merge `skills-import` → `main`
2. Document skills usage in README
3. Add integration tests for auto-loading
4. Consider adding more skill categories in future imports

---

_No ADR required - vendor copy method preserves original structure and attribution._

Last updated: 2026-03-04
