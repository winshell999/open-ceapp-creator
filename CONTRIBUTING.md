# Contributing

## Repository boundary

`open-ceapp-creator` is an independent public repository. Do not vendor it into the CanEngine source repository and do not copy CanEngine internal handoff, deployment, certificate, database, or production configuration documents into this repository.

When a CanEngine host change affects CEAPP authors, translate only the public contract into this repository: supported Host Bridge behavior, manifest requirements, compatibility notes, and public-safe examples.

## Development flow

1. Start from an up-to-date `main` branch.
2. Create a focused branch such as `feature/...`, `fix/...`, or `maintenance/...`.
3. Preserve the CEAPP's own version lifecycle. Do not bump a CEAPP or Skill version merely because the CanEngine host version changed.
4. Add only the minimum Host Bridge permissions needed by a user-visible feature.
5. Keep browser fallbacks where practical, but validate host-dependent behavior inside CanEngine.
6. Do not add remote first-screen CSS, JavaScript, fonts, or icon dependencies to the starter.
7. Do not invent undocumented `window.CanEngine` methods or manifest permissions.

## Required checks

Before a commit or pull request:

```bash
python3 scripts/audit_public_repo.py
python3 scripts/validate_ceapp.py assets/starter
python3 -m py_compile scripts/validate_ceapp.py scripts/audit_public_repo.py
node --check assets/starter/app.js
node --check assets/starter/assets/ceapp-i18n.js
git diff --check
```

Also test the relevant workflow in a normal browser and, when it uses Host Bridge functionality, in CanEngine.

## Documentation rules

Public documentation should explain what a CEAPP can depend on, not how CanEngine is privately implemented.

Good content:

- `window.CanEngine` public behavior
- manifest and permission requirements
- browser/host fallbacks
- Phone Bridge application intake patterns
- package-safe asset handling
- compatibility and validation rules

Do not include:

- private Go/Wails implementation paths when they are not necessary for CEAPP authors
- production hostnames or internal network topology
- database schemas used only by CanEngine services
- signing certificates, team identifiers, notarization profiles, or deployment credentials
- live request/response examples containing tokens or user data

## Pull request scope

Keep changes reviewable. A documentation correction should not silently restructure the starter. A starter change should update the corresponding reference and validator when the public contract changes.
