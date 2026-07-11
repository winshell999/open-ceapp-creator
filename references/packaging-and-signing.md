# CEAPP Packaging and Signing Handoff

This open Skill creates CEAPP source projects. CanEngine validates, packages, and signs the final container.

## Current public flow

1. Finish and validate a clean CEAPP project root.
2. Confirm the root contains `app.json`, `index.html`, local CSS/JS, and only required runtime assets.
3. Open CanEngine.
4. Go to `我的 → 开发者身份 / CEAPP打包与签名`.
5. Choose or drag the **project root directory** into the packaging area.
6. Review validation and source information.
7. Let CanEngine package and sign the project with the currently authorized identity.
8. Save the versioned `.ceapp` output and test importing it on the intended platform.

The current public packaging screen accepts a CEAPP project directory. Do not document existing `.ceapp` re-signing as a supported public flow.

## Source and trust language

- A valid signature proves package integrity and identifies the signing source.
- A signature does not prove that the app logic passed a security or privacy audit.
- An unsigned or invalidly signed package requires extra caution.
- Do not promise a specific source badge or trust level; CanEngine determines it from the authorized identity and package state.

## Never include

- official or publisher private keys
- private-key filesystem locations
- reusable signing tokens or passwords
- hard-coded key IDs presented as public signing credentials
- scripts that impersonate an official or trusted publisher
- statements that describe self-signing as official certification

Public identifiers such as a displayed publisher ID or key ID cannot sign a package by themselves, but they still do not belong in a generic starter unless the user supplies them for a legitimate project.

## Final checks

Before handing the project to CanEngine:

1. Run `python3 scripts/validate_ceapp.py /path/to/project` from this Skill.
2. Confirm the project version comes from its own `app.json`, not the CanEngine host version.
3. Confirm a versioned output name will be used, such as `my-app-1.2.0.ceapp`.
4. Confirm the source root has no `.env`, archives, old packages, private notes, design sources, or build caches.
5. Confirm no secret, absolute user path, private network detail, session URL, or internal endpoint is present.
6. Test the installed package in CanEngine, including locale, offline first screen, package media, denied permissions, and upgrade behavior.
