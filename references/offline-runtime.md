# Runtime Strategy And Offline Rules

## Choose A Runtime Strategy First

Every ceapp should explicitly choose one of these:

1. `offline-strict`
2. `hybrid-online`
3. `online-first`

This choice affects how much local bundling, fallback handling, and dependency disclosure the app needs.

## `offline-strict`

Use when:

- the app should remain useful without network access
- first paint must be stable for distributed desktop users
- the user explicitly wants offline-safe startup

Rules:

- the app must open its UI without requiring the network
- core workflow must not depend on remote CSS / JS
- critical icons, images, fonts, and templates must be local
- network use is allowed only as an enhancement

## `hybrid-online`

Use when:

- the shell UI should boot locally
- but remote APIs, templates, model calls, or content may be required
- the app should degrade gracefully when the network is weak or unavailable

Rules:

- shell UI, local routing, and basic interactions should still boot locally
- remote APIs and content may be required for full usefulness
- loading, retry, and failure states are mandatory
- there must be a meaningful degraded state instead of a silent blank area

## `online-first`

Use when:

- the user explicitly says offline support is not needed
- the app is mainly a remote service entrypoint
- strict local mirroring would add unnecessary complexity

Rules:

- remote CSS / JS / images may be acceptable if the user explicitly chose this mode
- you may skip heavy offline hardening work
- but the app still needs:
  - a nonblank startup shell
  - visible loading
  - timeout / error / retry behavior
  - a clear statement of remote dependencies

If the user does not choose, prefer `offline-strict` or `hybrid-online` over `online-first`.

## Do Not Ship

- `https://cdn.tailwindcss.com`
- remote React/ReactDOM/Babel scripts
- remote CSS frameworks
- remote icon libraries
- remote Google Fonts or other hosted fonts for first paint

These are hard bans for `offline-strict`.

For `hybrid-online`, local shell assets are still preferred even if remote data/content is required.

For `online-first`, remote startup assets may be acceptable when the user has explicitly accepted the tradeoff, but blank-screen startup and silent failure are still unacceptable.

## Acceptable Patterns

- local `index.html` + `styles.css` + `app.js`
- bundled Vite/React build with local emitted files
- locally bundled fonts, icons, images, and helper scripts
- `assetURL(appId, "assets/file.png")` for package-local images, audio, and video when running inside CanEngine
- `assetDataURL(appId, "assets/file.png")` only for small inline assets or clipboard/copy workflows
- inline critical CSS if it keeps the package simpler

## Current Host Reality

Apps do not run as standalone browser tabs in production. They run inside the current CanEngine host launch flow:

- launch HTML is prepared by the host
- bridge access is injected
- local file base paths are important
- rendering happens in the system webview layer, not in a bundled full Chrome runtime

Current practical expectation:

- macOS behaves like a WKWebView / WebKit-family host
- Windows behaves like a WebView2 / Chromium-family host

That means offline work is not just “does this HTML open in Chrome”. It is also:

- does it still render inside the host iframe launch path
- do packaged assets survive import/install and resolve through the host bridge
- do local scripts/styles still resolve after import and install
- does layout or interaction avoid webview-only compatibility regressions

## Local Media Loading

For package-local images, audio, and video, prefer this order:

1. `window.CanEngine.assetURL(appId, assetPath)` for normal display/playback.
2. `window.CanEngine.assetDataURL(appId, assetPath)` only for small inline resources or clipboard/copy workflows.
3. Relative paths such as `assets/demo.png` only as a standalone-browser fallback.

Avoid using `assetDataURL` for videos, audio, or large images. It duplicates the whole file into a base64 string and can waste significant memory.

## Packaging Hygiene

When the app folder contains extra materials such as:

- `OLD/`
- `demo/`
- archives
- design handoff folders

do not pack the folder wholesale. Stage a clean temporary package source directory containing only:

- `app.json`
- `index.html`
- `styles.css`
- `app.js`
- `assets/`
- `scripts/` when truly needed at runtime

## Verification

Before finishing:

1. Confirm the selected runtime strategy is documented truthfully.
2. Confirm whether the app should rely on shared CanEngine runtimes via `runtime.requirements` instead of shipping its own install flow.
3. If the app is `offline-strict`, disconnect from the network or reason as if the network is unavailable.
4. Confirm the app’s initial UI still renders.
5. Confirm package-local images, audio, and video render through CanEngine with `assetURL`.
6. Confirm large media is not converted to `data:` URLs unless the user explicitly needs inline data.
7. Confirm buttons, menus, and client-side flows still work for the local parts of the app.
8. If the app is not `offline-strict`, confirm loading, timeout, and retry behavior exist for remote dependencies.
9. Confirm the app still launches through CanEngine, not only in a direct browser open.

## Recommendation

For internal tools and first-party CanEngine apps, prefer simple local assets over runtime CDN convenience. Packaging reliability matters more than shaving a few setup minutes.
