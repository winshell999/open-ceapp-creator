---
name: open-ceapp-creator
description: Use this skill when creating or updating a public CanEngine CEAPP source project that can be packaged and signed by the CanEngine client. This skill generates standard CEAPP project files, local assets, bilingual support, and host-bridge compatible code; it does not create official/KOL signatures or final trusted distribution packages.
---

# open-ceapp-creator

Use this skill for public-facing CanEngine application source work. It is the open version of the CEAPP starter workflow and is designed for external developers, creators, and KOL partners who want to generate a clean CEAPP project directory that can later be packaged and signed inside CanEngine.

## Scope Boundary

This skill is responsible for:

- generating a CEAPP project root directory
- creating or updating `app.json`, `index.html`, CSS, JS, local assets, and docs
- keeping the project compatible with CanEngine host bridge conventions
- keeping the project offline-safe where practical
- preparing the project so it can be dragged into CanEngine for packaging and signing

This skill is not responsible for:

- generating final official `.ceapp` distribution packages
- generating KOL-signed packages
- storing or using CanEngine official private keys
- storing or using KOL private keys
- providing trusted publisher certification
- bypassing CanEngine packaging/signing flows

Final `.ceapp` packaging and source-label signing must be done by CanEngine:

`CanEngine → 我的 → 开发者身份 / CEAPP打包与签名 → 拖入CEAPP项目根目录 → 打包并签名`

## Defaults

Unless the user explicitly asks otherwise, build with these assumptions:

- The output is a CEAPP source project, not a pre-signed final package.
- The app works offline after install.
- The first screen does not depend on any CDN asset.
- The project supports both `zh-CN` and `en-US`.
- When hosted inside CanEngine, the app follows the platform locale automatically.
- When opened outside CanEngine, the app falls back to its own saved locale or `navigator.language`.
- Static assets stay inside the project directory.
- The project root is clean enough to be dragged into CanEngine for packaging.

## First Choice

Pick the lightest runtime that fits:

- Prefer `assets/starter/` for simple tools, utilities, demos, and operator workflows.
- Use a bundled framework build only when the UI really needs React, Vue, or another frontend stack.
- If a framework is used, the shipped `index.html`, CSS, JS, icons, images, and fonts must all be local files.

## Read These References

- `references/bilingual-framework.md`: locale flow, message tables, and bilingual structure
- `references/offline-runtime.md`: offline packaging hygiene and asset expectations
- `references/manifest-and-host-bridge.md`: `app.json` and `window.CanEngine` bridge usage
- `references/phone-bridge.md`: public-safe Phone Bridge usage for CEAPP source projects
- `references/packaging-and-signing.md`: how generated projects are packaged and signed by CanEngine

## Workflow

1. Start from `assets/starter/` or mirror its structure.
2. Keep the first runnable version dependency-light.
3. Put user-facing strings in a central message table.
4. Use `nameI18n` and `descriptionI18n` in `app.json` so the CanEngine app list localizes correctly.
5. When running inside CanEngine, use the host bridge locale API:
   - `getLocale()`
   - `onLocaleChange(handler)`
   - `setLocale(locale)` only when the app is intentionally changing the host language
6. For local media assets, prefer:
   - `assetURL(appId, path)` for `<img>`, `<audio>`, and `<video>`
   - `assetDataURL(appId, path)` for small inline or copy workflows
7. For file inputs, support normal picker flow first and add drag/drop or clipboard when the task benefits from it.
8. Keep the CEAPP source root clean and self-contained.
9. If the app needs phone-to-desktop intake, prefer the system `window.CanEngine.phoneBridge` APIs instead of inventing a custom LAN upload server inside the CEAPP.
10. Do not create official, KOL, or trusted signatures in the skill output.

## Rules

- Never ship a CEAPP source project whose first screen depends on remote CSS or JS.
- Never use `cdn.tailwindcss.com`, remote React UMD bundles, remote icon fonts, or remote Google Fonts in the shipped project.
- Bundle fonts locally when needed.
- Keep locale names stable: `zh-CN` and `en-US`.
- Do not tie CEAPP app versions to the CanEngine host version.
- Prefer simple static HTML/CSS/JS when that is enough.
- Keep `window.CanEngine` integration graceful: the app should still be debuggable in a normal browser when practical.
- Do not include private keys, signing secrets, official key IDs, KOL key IDs, or default trusted publisher credentials in generated projects.
- Do not embed private local IPs, hard-coded session tokens, raw filesystem paths, or internal-only debugging endpoints in public CEAPP source.
- Do not describe self-signing as official certification or security review.

## Packaging Handoff

After app changes:

1. Update the CEAPP source directory.
2. Rebuild any local frontend bundle if the app uses one.
3. Validate that the project root contains the required files, especially `app.json` and `index.html`.
4. Open CanEngine and go to `我的 → 开发者身份 / CEAPP打包与签名`.
5. Drag the CEAPP project root folder into the packaging area.
6. Let CanEngine package and sign it using the current authorized identity.

Expected label behavior after CanEngine signing:

- Official signer: green `官方` label.
- KOL signer: blue KOL display-name label, such as `仙人掌`.
- Normal local signer: yellow user-name label, such as `王灿`, indicating self-signed / lower trust.
- Unsigned package: gray `未签名` label.
- Invalid signature: red `签名无效` label.

The labels are for source identification and risk signaling only. They are not a security audit of the app logic.
