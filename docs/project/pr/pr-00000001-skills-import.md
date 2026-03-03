---
# PR-00000001: Import agent skills from borealBytes/ag-skills into repo

| Field               | Value |
| ------------------- | ----- |
| **PR**              | `#00000001` |
| **Author**          | Automated agent (assistant) |
| **Date**            | 2026-03-03 |
| **Status**          | Open |
| **Branch**          | `skills-import` → `main` |
| **Related issues**  | N/A |
| **Deploy strategy** | Standard |

---

## 📋 Summary

### What changed and why

This PR (record) initiates the planned import of agent skills from the public repository `https://github.com/borealBytes/ag-skills/tree/main/skills-content` into this repository using the Agent Skills IO format (https://agentskills.io/home). The goal is to ensure these skills are available and always referenced by this repo when agent functionality is used.

### Impact classification

| Dimension | Level | Notes |
| --- | --- | --- |
| **Risk** | 🟡 Medium | Repo integration work, but non-destructive initially (adds files and loaders). |
| **Scope** | Narrow → Moderate | Adds a `skills/` import area and loader logic; may touch bootstrapping code later. |
| **Reversibility** | Easily reversible | Can remove the `skills/` directory and loader changes. |
| **Security** | Low | We'll scan imported dependencies and check license. |

---

## 🔍 Changes (Planned)

### Change inventory

| File / Area | Change type | Description |
| --- | --- | --- |
| `skills/` | Added | Vendor/imported skills content from `borealBytes/ag-skills` (selected subset). |
| `scripts/` or `src/` | Added/Modified (future) | Add a skills loader that checks for agent skills at runtime and prefers them first. |
| `docs/project/pr/pr-00000001-skills-import.md` | Added | This PR record (you are reading it). |

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

## Next steps (this PR's immediate plan)

1. Audit the public repo and list skill files to import. (In progress)
2. Decide integration method (vendor copy, subtree, or submodule). Recommend vendor-copy into `skills/` for portable, offline usage. (decision pending)
3. Implement import script and add loader registration. (future PR commits on this branch)
4. Run `./scripts/ci-local.sh` and add tests. (verification)

---

_No ADR required at this stage. If a durable architecture decision is made (submodule vs vendor vs package), an ADR will be added._

Last updated: 2026-03-03
