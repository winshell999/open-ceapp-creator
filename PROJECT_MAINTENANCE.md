# Project Maintenance

## 1. Independence from CanEngine

This repository is a public CEAPP authoring project, not a mirror, submodule, subtree, or release artifact of the CanEngine source repository.

Keep the directory and Git repository independent. The parent workspace may contain other repositories, but `open-ceapp-creator/.git` is the only Git root for this project.

Do not add the CanEngine source repository as a nested working tree. Do not use a CanEngine production remote as this repository's `origin`.

## 2. Version model

There are three different versions and they must not be conflated:

- **open-ceapp-creator release version**: version of this public repository/Skill distribution.
- **starter CEAPP version**: `assets/starter/app.json -> version`; the starter has its own app lifecycle.
- **minimum CanEngine version**: `minCanEngineVersion`; bump only when the starter actually depends on a newer host capability.

A CanEngine host release does not automatically require a repository or starter version bump.

## 3. Host contract synchronization

When CanEngine changes:

1. identify whether the change affects public CEAPP behavior;
2. verify the public `window.CanEngine`/manifest contract;
3. update the smallest relevant reference document;
4. update starter code only when the starter uses that feature;
5. update validators/tests if a new invariant can be checked automatically;
6. do not copy internal implementation maps, production endpoints, credentials, deployment guides, database details, or signing infrastructure into this public repository.

As of the current public sync, Phone Bridge remains a host-level system capability. A CEAPP uses the Host API and should not create its own LAN transfer service.

## 4. Git model

Recommended branches:

- `main`: stable public baseline
- `feature/<name>`: new public capability/example
- `fix/<name>`: focused bug fix
- `maintenance/<name>`: repository hygiene, docs, validation, CI

Before switching branches with local changes, stash or commit a local checkpoint. Avoid detached-HEAD development.

Do not force-push `main` as routine maintenance. Do not rewrite published history merely to clean a credential: rotate/revoke the credential first, then perform history cleanup only when there is a clear reason and coordinated plan.

## 5. Authentication

Keep Git credentials outside the repository. A normal remote looks like:

```text
https://github.com/<owner>/<repo>.git
```

or an SSH equivalent. It should not embed a password or personal access token.

## 6. Release gate

Before publishing a branch/tag/release:

```bash
python3 scripts/audit_public_repo.py
python3 scripts/validate_ceapp.py assets/starter
python3 -m py_compile scripts/validate_ceapp.py scripts/audit_public_repo.py
node --check assets/starter/app.js
node --check assets/starter/assets/ceapp-i18n.js
git diff --check
git status --short
```

Then manually review:

- repository diff and untracked files
- permissions and manifest changes
- new public Host Bridge statements
- user-facing Chinese and English copy
- secrets/private paths/internal implementation leakage
- CanEngine-host behavior for any bridge-dependent change

## 7. Update discipline

Prefer small, reviewable updates. When a host capability changes, update the reference and regression check in the same change. If a statement is based on an internal handoff but is not part of the public CEAPP contract, leave it out of this repository.
