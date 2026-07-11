---
name: open-ceapp-creator
description: Create or update a public, package-ready CanEngine CEAPP source project with an offline-capable local shell, zh-CN/en-US localization, minimal app.json permissions, browser-safe fallbacks, and current Host Bridge patterns. Use when generating a new CEAPP, improving an existing CEAPP, adding AI/Data/Phone/Notification/file/job integrations, or preparing a clean project folder for CanEngine packaging and signing. Do not use it to create official/KOL signatures or embed private credentials.
---

# Open CEAPP Creator

Create a clean CEAPP source project that another developer can understand, test, and package in CanEngine. Optimize for one useful product flow, not maximum bridge coverage.

## Public boundary

Produce source files only. Do not generate or claim:

- an official, KOL, or trusted signature
- a final trusted distribution package
- publisher private keys, signing secrets, or reusable credentials
- private IP addresses, session URLs, tokens, absolute user paths, or internal endpoints

Use CanEngine's packaging and signing screen for the final `.ceapp`. Read `references/packaging-and-signing.md` before handing off packaging instructions.

## Start with context

1. Inspect the target directory before editing. Preserve unrelated user changes.
2. If running in a CanEngine Canvas with Local MCP V2, call `get_work_context` once for the active Canvas, profile, permissions, limits, and selected Skill summaries. Read selected Skill content only through `read_selected_skills` and `read_skill_file`; do not guess a Canvas ID or read a Skill through ordinary project-file APIs.
3. Write a one-sentence product contract: **user + task + finished result**.
4. Choose a runtime strategy from `references/offline-runtime.md`. Default to `offline-strict`; use `hybrid-online` only when remote data or AI is part of the product.
5. Choose the lightest implementation. Prefer local HTML/CSS/JS for small tools. Use a framework only when state or UI complexity justifies a local bundled build.

## Build the useful core

1. Copy `assets/starter/` for a new project.
2. Replace every starter identity consistently:
   - directory name
   - `app.json` `appId`, names, descriptions, and version
   - JavaScript `APP_ID`
   - Data Bridge collection names and database filename
   - icon and visible product copy
3. Keep `appId` stable after users have data. Changing it creates a different app/data identity.
4. Keep the CEAPP version independent from the CanEngine host version.
5. Implement one complete local workflow before optional bridges. Include its empty, loading, success, and error states.
6. Keep the first screen useful without remote CSS, JavaScript, fonts, icons, or content.

The starter intentionally declares only app-private Data Bridge read/write access. Remove Data Bridge if the product does not persist data. Do not retain sample features or permissions that the final product does not use.

## Add capabilities on demand

Read `references/manifest-and-host-bridge.md` before changing `app.json` or calling `window.CanEngine`.

For every capability added:

1. Add the exact `capabilities` metadata when the schema requires it.
2. Add only the matching flat permission strings.
3. Detect the method before calling it.
4. Provide a useful unavailable/error state.
5. Add one visible operation that verifies the integration.
6. Remove the capability and permission if the final UI never calls it.

Additional routing:

- Read `references/phone-bridge.md` only when accepting or sending Phone Bridge files.
- Read `references/bilingual-framework.md` before changing locale structure or user-facing copy.
- Read `references/offline-runtime.md` when adding remote APIs, frameworks, fonts, or runtime dependencies.

## Follow the standard interaction patterns

- Resolve the bridge lazily from `window.CanEngine` or `window.parent.CanEngine`.
- Treat CanEngine locale as the source of truth. Do not add an app-level locale switch to an ordinary app.
- Keep all user-facing text in both `zh-CN` and `en-US` message tables.
- Load package images/audio/video with `assetURL(appId, path)`; use relative URLs only as browser fallback.
- Use `assetDataURL` only for small inline or copy-only cases.
- Preview browser `File`/`Blob` objects with `URL.createObjectURL` and revoke old URLs.
- Stage in-memory files with `stageFile({ appId, name, dataBase64, mime })`.
- Stage host-native drops with `stageFile({ appId, sourcePath })`.
- Normalize picker, browser drop, paste, native drop, and Phone Bridge input before business logic.
- Use `data.local(collection).get/find/put/delete` for app-private persistence; use `localStorage` only as a browser-debug fallback or an explicitly designed cache.
- Never request API keys inside a CEAPP. AI provider configuration stays in CanEngine.

## Keep the project root clean

Package only runtime files:

```text
my-app/
├── app.json
├── index.html
├── app.js
├── styles.css
├── assets/
│   ├── ceapp-i18n.js
│   └── logo.png
├── data/                 # only when a local schema is declared
│   └── localdb.schema.json
└── scripts/              # only when a declared command needs them
```

Do not package design sources, archives, screenshots, old builds, private notes, `.env` files, or unrelated docs.

## Validate before handoff

Run the bundled public-source validator:

```bash
python3 scripts/validate_ceapp.py /path/to/ceapp-project
```

Then verify manually:

1. The useful core works in a normal browser.
2. The app launches inside CanEngine with no blank first screen.
3. Host locale changes rerender visible copy.
4. Package media loads through `assetURL`.
5. Every permission maps to code and a user-visible feature.
6. Optional bridges fail gracefully when disabled or denied.
7. Keyboard focus, labels, empty states, and reduced motion are usable.
8. No secret, personal path, private network detail, session URL, or internal endpoint is present.
9. `app.json` and JavaScript use the same `appId`.
10. The final project folder contains only files required at runtime.

Fix validation failures before packaging. Treat warnings as review prompts; do not silence them without checking the source.

## Packaging handoff

Hand the clean project root to CanEngine:

`CanEngine → 我的 → 开发者身份 / CEAPP打包与签名 → 选择或拖入项目根目录 → 检查 → 打包并签名`

Describe a signature as source/integrity metadata, not a security audit. Current public packaging accepts a CEAPP project root; do not tell users that this flow re-signs an existing `.ceapp`.
