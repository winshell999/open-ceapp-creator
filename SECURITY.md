# Security Policy

This repository is intentionally public. Keep the boundary simple: it may document CEAPP-facing contracts and public integration patterns, but it must not contain CanEngine private implementation details or reusable credentials.

## Never commit

- API keys, access tokens, cookies, passwords, OAuth client secrets, private keys, signing keys, or reusable authorization codes
- live Phone Bridge session data, QR payloads, pairing codes, device identifiers, private IP addresses, or user filesystem paths
- production-only endpoints, internal debug URLs, raw diagnostics, or private deployment instructions
- official/publisher signing material or instructions that bypass CanEngine packaging and signing
- `.env` files, generated `.ceapp` packages, local logs, IDE state, or operating-system metadata

Public product websites, public documentation URLs, public repository identifiers, and non-secret example IDs are allowed when they are intentionally public.

## Local authentication

Keep Git authentication outside repository URLs and tracked files. Prefer the operating-system credential manager or a GitHub CLI/login flow. The `origin` URL should remain a normal credential-free HTTPS or SSH URL.

Do not paste a personal access token into `.git/config`, scripts, documentation, shell examples, or source files.

## Before every push

Run:

```bash
python3 scripts/audit_public_repo.py
python3 scripts/validate_ceapp.py assets/starter
node --check assets/starter/app.js
node --check assets/starter/assets/ceapp-i18n.js
git diff --check
git status --short
```

A successful automated scan reduces risk but does not replace manual review.

## Reporting a security issue

Do not open a public issue containing a secret, live session, user path, private endpoint, or exploit payload. Contact the repository owner through a private channel first and include only the minimum information required to reproduce the problem.

If a credential was ever committed or embedded in a Git remote, removing the text is not enough: revoke or rotate that credential at its provider.
