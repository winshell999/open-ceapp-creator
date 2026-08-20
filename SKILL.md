---
name: open-ceapp-creator
description: Create or update a public, package-ready CanEngine CEAPP source project with an offline-capable local shell, zh-CN/en-US localization, minimal app.json permissions, browser-safe fallbacks, and current Host Bridge patterns. Use when generating a new CEAPP, improving an existing CEAPP, adding AI/Data/Phone/Notification/file/job integrations, or preparing a clean project folder for CanEngine packaging and signing. Do not use it to create trusted signatures, expose private implementation details, or embed credentials.
---

# Open CEAPP Creator

Create a clean CEAPP source project that another developer can understand, test, publish, and package in CanEngine. Optimize for one useful product flow, not maximum bridge coverage.

## Public boundary

Produce public-safe source files only. Do not generate or expose:

- official, publisher, or trusted signing secrets
- a final trusted distribution package
- private keys, signing tokens, reusable credentials, or real user licenses
- private IP addresses, live session URLs, QR/pairing payloads, device identifiers, or absolute user paths
- production-only endpoints, internal deployment instructions, database details, or private CanEngine implementation maps

Public product/documentation URLs and public repository identifiers are fine when intentionally public.

Use CanEngine's packaging and signing screen for the final `.ceapp`. Read `references/packaging-and-signing.md` before packaging handoff.

## Start with context

1. Inspect the target directory before editing. Preserve unrelated user changes.
2. If running in a CanEngine Canvas with Local MCP V2, read the active work context first. Use the exact Canvas ID supplied by the task for subsequent Canvas tools when the host requires explicit IDs. Read selected Skill content only through the Skill reader; do not guess paths or Canvas IDs.
3. Write a one-sentence product contract: **user + task + finished result**.
4. Choose a runtime strategy from `references/offline-runtime.md`. Default to `offline-strict`; use `hybrid-online` only when remote data or AI is part of the product.
5. Choose the lightest implementation. Prefer local HTML/CSS/JS for small tools. Use a framework only when state or UI complexity justifies a local bundled build.
6. For any nontrivial Host Bridge work, read `references/ceapp-integration-pitfalls.md` before coding.

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
5. Implement one complete local workflow before optional bridges. Include empty, loading, success, and error states.
6. Keep the first screen useful without remote CSS, JavaScript, fonts, icons, or content.

The starter intentionally declares only app-private Data Bridge read/write access. Remove Data Bridge if the product does not persist data. Do not retain sample features or permissions that the final product does not use.

## Add capabilities on demand

Read `references/manifest-and-host-bridge.md` before changing `app.json` or calling `window.CanEngine`.

For every capability added:

1. Add exact capability metadata when the public schema requires it.
2. Add only matching flat permission strings.
3. Feature-detect the exact method before calling it.
4. Provide a useful unavailable/error state.
5. Add one visible operation that verifies the integration.
6. Remove capability metadata and permission if the final UI never calls it.

Additional routing:

- Read `references/phone-bridge.md` when accepting or sending Phone Bridge files.
- Read `references/bilingual-framework.md` before changing locale structure or user-facing copy.
- Read `references/offline-runtime.md` when adding remote APIs, frameworks, fonts, or runtime dependencies.
- Read `references/ceapp-integration-pitfalls.md` for browser-vs-host, native drop, Phone Bridge targeting, external navigation, and async lifecycle failures.

## Host Bridge rules

The fact that CanEngine desktop has a feature does **not** prove that a CEAPP can call it. The CEAPP contract is the capability actually exposed through `window.CanEngine` in the running host.

- Resolve the bridge lazily from `window.CanEngine` or a safe `window.parent.CanEngine` fallback.
- Never call `window.runtime.*` from CEAPP application code.
- Never invent methods such as `openBrowser()`, `openExternal()`, or `getLatestPhoneFile()` because the desktop host appears to have a similar feature.
- Manifest permissions do not create Host APIs; they only declare access to capabilities the host already supports.
- Show success only after the Host Bridge call succeeds.
- Keep browser fallback/degraded behavior where practical.

## Standard interaction patterns

- Treat CanEngine locale as the source of truth. `getLocale()` may be asynchronous; do not treat a Promise as a locale string.
- Keep all user-facing text in matching `zh-CN` and `en-US` message tables.
- Load package images/audio/video with `assetURL(appId, path)`; use relative URLs only as browser fallback.
- Use `assetDataURL` only for small inline or copy-only cases.
- Preview browser `File`/`Blob` objects with `URL.createObjectURL` and revoke old URLs.
- Stage in-memory files with `stageFile({ appId, name, dataBase64, mime })`.
- Stage host-native drops with `stageFile({ appId, sourcePath })`.
- Normalize picker, browser drop, paste, native drop, and Phone Bridge input before business logic.
- Capture stable application IDs/targets before starting asynchronous dialogs, transfers, AI jobs, or runtime jobs.
- Store and call unsubscribe handlers for Bridge events; do not register duplicate listeners every time a modal opens.
- Use `data.local(collection)` for app-private persistence; use `localStorage` only as browser-debug fallback or explicit cache.
- Never request API keys inside a CEAPP. AI provider configuration stays in CanEngine.

## Phone Bridge rule

Phone Bridge is a host-level system capability. A CEAPP must not create its own LAN transfer service for normal intake.

Most importantly:

**opening the Phone Bridge panel is not the same as importing a file into the current CEAPP target.**

For multiple targets, capture `targetId/purpose` first, establish the supported receive flow, then open Phone Bridge, read/normalize the host-managed file, and apply it back to the captured target. Do not infer the target from the currently selected DOM node after an asynchronous upload finishes.

## External navigation rule

A CEAPP runs in an embedded WebView, not a guaranteed top-level Chrome tab. If the current public Host Bridge does not expose a documented external-navigation method:

- use a normal HTTPS link;
- use `target="_blank"` / `rel="noopener noreferrer"` where appropriate;
- offer Copy Link fallback when useful;
- do not call private Wails/runtime APIs or shell commands from frontend JavaScript.

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

Do not package design sources, archives, screenshots, old builds, private notes, `.env` files, signing material, logs, or unrelated docs.

## Validate before handoff

Run the bundled CEAPP validator:

```bash
python3 scripts/validate_ceapp.py /path/to/ceapp-project
```

When working on this public repository itself, also run:

```bash
python3 scripts/audit_public_repo.py
```

Then verify manually:

1. The useful core works in a normal browser.
2. The app launches inside CanEngine with no blank first screen.
3. Host locale changes rerender visible copy.
4. Package media loads through `assetURL`.
5. Every permission maps to called code and a user-visible feature.
6. Optional bridges fail gracefully when unavailable, disabled, or denied.
7. Keyboard focus, labels, empty states, and reduced motion are usable.
8. No secret, personal path, private network detail, session URL, raw diagnostics, or internal endpoint is present.
9. `app.json` and JavaScript use the same `appId`.
10. The final project folder contains only files required at runtime.
11. Phone Bridge/file-drop/AI/notification/job workflows are tested inside CanEngine when used; Chrome-only success is insufficient.

Fix validation failures before packaging. Treat warnings as review prompts; do not silence them without checking the source.

## Packaging handoff

Hand the clean project root to CanEngine:

`CanEngine → 我的 → 开发者身份 / CEAPP打包与签名 → 选择或拖入项目根目录 → 检查 → 打包并签名`

Describe a signature as source/integrity metadata, not a security audit. Do not tell users that public source files can create official/trusted signing identities or bypass CanEngine authorization.
