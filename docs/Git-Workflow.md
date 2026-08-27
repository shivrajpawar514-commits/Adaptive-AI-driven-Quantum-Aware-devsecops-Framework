# Git Workflow Specification

This document outlines the branching strategy, commit naming guidelines, pull request reviews, and versioning rules for the repository.

---

## 1. Branch Strategy

We follow a structured multi-branch git workflow to organize concurrent development tasks:

```
        +------------------[ main ] (Stable Releases)
        |                     ^
        v                     | Release PR
   [ develop ] <--------------+---------+---------+---------+
        ^                               |         |         |
        | Feature Merge                 |         |         |
        +---------------+---------------+         |         |
                        |                         |         |
            [ backend/devam ]                     |         |
                                [ ai/dil ]        |         |
                                            [ security/kalpesh ]
                                                        [ quantum/shivraj ]
```

- **`main`**: The production branch containing stable release tags. No developer commits directly to main.
- **`develop`**: The integration branch. All feature branches are merged here for testing.
- **`backend/devam`**: Feature branch for Express APIs, MongoDB schemas, Docker packaging, and cloud infrastructure setup.
- **`ai/dil`**: Feature branch for AI pipeline modeling, PCA reduction scripts, and reconstruction loss validation.
- **`security/kalpesh`**: Feature branch for ECC signature validation, JWT sessions, OPA policies, and security audits.
- **`quantum/shivraj`**: Feature branch for Bloch Sphere modeling, Qiskit script benchmarks, and PQC migration studies.
- **`documentation`**: Minor updates to docs, markdown sheets, or project summaries.

---

## 2. Commit Naming Standards

Commits must follow the **Conventional Commits** format:

$$\text{<type>(<module>): <description>}$$

### Allowed Types
- **`feat`**: A new user-facing feature.
- **`fix`**: A bug fix.
- **`docs`**: Documentation updates.
- **`style`**: Formatting adjustments (e.g. spaces, semi-colons).
- **`refactor`**: Code changes that do not fix bugs or add features.
- **`test`**: Writing or correcting unit/integration tests.
- **`chore`**: Maintenance tasks, dependency updates, or git configurations.

### Examples
- `feat(auth): implement ecc challenge response signature verification`
- `fix(ai): resolve dimensions mismatch in autoencoder decoder layer`
- `docs(readme): update repository build instructions`

---

## 3. Pull Request & Merge Strategy

- **PR Requirements**: All merges into `develop` or `main` must occur via a Pull Request. PRs must pass unit test runners and static analysis audits.
- **Code Review**: PRs must be reviewed and approved by the Research Lead (Devam) or the module owner before integration.
- **Merge Style**: Squash-and-merge is preferred for feature branch merges into `develop` to keep a clean commit history. Merges to `main` must use merge commits to preserve release records.

---

## 4. Repository Versioning

We utilize Semantic Versioning (SemVer) 2.0.0 for stable releases:

$$\text{v<MAJOR>.<MINOR>.<PATCH>}$$

- **MAJOR**: Incompatible API modifications.
- **MINOR**: Backward-compatible functional enhancements.
- **PATCH**: Backward-compatible bug fixes or doc changes.
- **Pre-releases**: Tagged with suffixes (e.g. `v0.1.0-alpha.1`).
