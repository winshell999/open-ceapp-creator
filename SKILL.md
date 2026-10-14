---
name: open-ceapp-creator
metadata:
  version: "1.8.0"
description: Create, debug or refactor CanEngine CEAPP source projects, including a quick form-prefill CEAPP from a website URL. For website form filling, research the actual fields and generate a local runtime.web app using the controlled CanEngine 1.8.0 browser.prefill JSON bridge. Also support local HTML tools, persistent local Web backends, remote website apps and optional Python compilation. Use verified public APIs and least privilege. Deliver source, validation evidence and native acceptance records without invented selectors, bypassing verification or submitting forms.
---

# Open CEAPP Creator

Generate from verified contracts and tested components, not from remembered API names.
Treat this skill as an executable generation workflow. Do not deliver a plan alone when asked for an app.

## Deliverables

Return a clean CEAPP source directory, a validation report, and a completed/pending native acceptance record.
When updating this skill itself, return the complete `skill.zip`.
The user-authorized current version is **1.8.0** for CanEngine, this skill, CEAPP templates and new-project defaults. Preserve existing host/build/app versions and minCanEngineVersion exactly. **Never increment or otherwise change any version for a feature, fix, packaging or test without an explicit user instruction.** If the user supplies a version, use that exact value consistently across source, manifests, UI, documentation and artifacts. Check the actual matching implementation rather than inferring capability from a version string. Do not manufacture official/KOL signatures.

## Start with evidence

1. With a supplied Canvas ID, first call `get_work_context_for_canvas` with that exact ID, confirm the returned ID, then use the same explicit ID on every Canvas operation.
2. Read the selected UI skill and existing project entry/manifest/dependencies before editing. Back up changed files, preserve unrelated files and signer/license boundaries.
3. Read `references/source-baseline.md` and `references/manifest-and-host-bridge.md`.
4. Locate the user's handoff/current source through authorized Canvas tools. Resolve any disagreement against the public `window.CanEngine` implementation and the relevant Go types/runner. Do not use private source paths as shipped configuration.
5. Record source version/date/hash and the methods actually consumed. If source is unavailable, use this snapshot conservatively and state that it was not refreshed. Do not invent methods to fill a gap.
6. Distinguish the authoring MCP tools from the CEAPP runtime. A connector exposed to the AI is not automatically an app bridge. Never call arbitrary Wails/Go internals from CEAPP code.

## Select a narrow profile

Decide the runtime mode before generating. **Website URL + quick-fill/prefill intent selects `form-prefill` first**, including Chinese requests such as “网站+SKILL”, “一键填写” and “快速预填”. Read `references/form-prefill.md` and implement that workflow. A URL alone without prefill intent selects remote website mode for reuse of a deployed service, unless local code or Host Bridge integration is requested. An explicit choice already made by the user does not need reconfirmation. Read `references/web-app-modes.md`.

| Mode | Minimum Host | Creation contract |
|---|---|---|
| Local HTML + jobs | Match used Bridge features | Package entry/assets; declare real jobs or the existing static-only inert command |
| Persistent local website | 1.8.0 | `runtime.web`; packaged backend entry; commands may be empty; permissions, writable data and sandbox setup matter |
| Remote website | 1.8.0 | `runtime.remoteWeb`; URL and independent storage, embedded in the host's right pane; entry may be omitted; no local commands, HTML, runtimes or Host Bridge |
| Protected remote website | 1.8.0 matching build | Same remote mode plus `runtime.remoteWeb.authorization: "canengine"`; registered website identity and server-side ticket verification |
| Website form prefill | 1.8.0 | Local `runtime.web` UI calls `CanEngine.browser.prefill(JSON)`; separate native right-pane website; signed fixed HTTPS targets and `browser.form.prefill` permission |

Remote mode is deliberately online. Do not force offline first paint, a local wrapper, dummy scripts or the Bridge Lab into it. Explain internet dependence and website-defined persistence in its metadata/docs. CanEngine UI is bilingual; the remote site's own language remains site-controlled. On macOS this mode needs 14+; Windows amd64 needs WebView2 and native acceptance. Do not claim Linux support.

Use the smallest matching profile from `scripts/create_ceapp.py`:

| Profile | Included workflow |
|---|---|
| `minimal` | Local shell, website/clipboard/print hooks, diagnostics |
| `files` | Native/bounded browser input, staged-file opening, folder selection |
| `python` | Files, declared Python script, runtime gate, cancel, managed results |
| `ai-text` | Host AI status and text generation only |
| `ai-media` | Files, text, vision, image, video and 3D task lifecycle |
| `data` | App-private local collection CRUD, optionally exact shared resource IDs |
| `phone` | Session/workbench, receive/import, explicitly confirmed phone send |
| `notifications` | Immediate test notification and bridge settings |
| `full` | Bridge Lab acceptance workbench, not the default for a business app |
| `web-python` | 1.8.0 persistent local HTTP demo, SQLite/data lifecycle and restricted Web Bridge |
| `remote-web` | 1.8.0 manifest-only website source, local icon and per-app browser storage |
| `form-prefill` | 1.8.0 local field-entry UI, researched JSON mapping, controlled native website prefill and manual review |

```bash
python scripts/create_ceapp.py --app-id my-file-tool --name "My File Tool" --profile python --output /path/to/new-project
python scripts/validate_ceapp.py /path/to/new-project --report /path/to/validation.json
python scripts/create_ceapp.py --app-id my-website --name "My Website" --profile remote-web --url https://example.com/app/ --storage persistent --output /path/to/new-website-app
```

For shared data, pass the real `--dataset` / `--action` IDs; the generator synchronizes manifest and configuration. Never seed a required imaginary dataset. Existing output directories are intentionally refused.

For requests such as “only in CanEngine”, “别人拿到网址也打不开” or “统一授权码”, read `references/remote-web-authorization.md`. Generate `remote-web --authorization canengine` with the registered fixed entry and minimum matching host 1.8.0. A valid formal license covers all registered protected apps; trials are denied. The website must verify tickets on its server before serving protected content; a manifest, User-Agent or frontend JS check cannot provide this protection. For a small PHP site, prefer one homepage handling the handshake and content; use an `index.php/` PATH_INFO entry only after verifying that the server supports it. Website PHP, service keys and session storage stay outside the CEAPP source. Public skill examples use reserved example domains and synthetic identities; never copy live site configuration, credentials, cookies, private paths or acceptance screenshots into this open-source skill or its ZIP.

## Website to prefill CEAPP

When given a website and this skill, start with the website research; do not require the user to supply selectors or author JSON. Use reasonable defaults for a new app: a focused bilingual local UI, memory-only entry, one fixed target, no optional permissions or profile storage. Ask only for an inaccessible target, indispensable business choices or missing authorized information while completing independent work.

1. Inspect the actual authorized page and record a value-free field map: unique scope/selector, native kind, format, exact option values, dependencies and verified event behavior. Never guess selectors from labels or the URL. Mark unsupported/protected components for manual handling.
2. Build a schemaVersion 1 request with synthetic fixture values. Run `form-prefill` generation with the researched HTTPS page and `--mapping`; see the exact command and contract in `references/form-prefill.md`. Runtime JSON references a target ID; the signed manifest supplies the URL.
3. Customize the field labels, options, format hints and business UI. Clear fixture defaults before delivery. Preserve an existing SQLite schema and traveler/customer management if present; read only the selected record through its existing controlled local interface. New persistence is opt-in, not a prefill prerequisite.
4. Call the public `CanEngine.browser.prefill(request)` only after a user click. Handle loading, single-flight, denied permission, `ok:false`, field reports and unknown outcomes. The host waits and verifies; do not write a second arbitrary JS automation bridge. Do not retry unresolved fills or overwrite later manual edits.
5. Run source/schema/HTTP/UI gates, then install and test in actual CanEngine with synthetic data. Verify native right-pane opening, field readback, manual editing, returning to the app, reload, structure-change fallback, protected fields and owner close. Report macOS and Windows independently. Keep CAPTCHA, consent and final submission manual.
6. Deliver source, mapping evidence, checks and native acceptance status; use the authorized signing flow for an installable package. A general browser preview or inherited MDAC test is not this website's native acceptance.

Do not use runtime.remoteWeb as the calling app, a cross-origin iframe, Tampermonkey, an external-browser handoff, Wails internals, arbitrary evaluate/JS, or undocumented DOM-read APIs. The remote page receives no Host Bridge. Keep values out of URLs, logs, diagnostics, localStorage and packaged examples; send them only through the local controlled request in memory. The standard-form contract has limits; new domains require declaration/approval and unsupported widgets require a separately reviewed host adapter or manual entry.

## Build by reusing components

Copy the generated project, then change business logic, message tables and the relevant panels. Existing local HTTP projects should retain their frontend/routes and use the host's `ceapp-web` generator described in `references/local-web-runtime-1.8.0.md`; do not transplant them into the Lab.
The adapter/recipes rules below apply to the local HTML profiles. Local Web gets only its restricted Web Bridge; remote websites get no Host Bridge. Never inject the static adapter into an arbitrary remote page.
Use `assets/starter/assets/ce-bridge.js` for host resolution, bound calls, mutations, runtime checks, jobs and data stores.
Use `assets/starter/assets/recipes.js` for AI/data/phone workflows.
Read `references/demo-catalog.md` for nine complete demos and opt-in low-level examples.
Do not copy `tests/` or simulated hosts into a distributable app.

Treat the Lab as a functional reference, not an app customers must inherit. For a single-purpose app, replace the Lab navigation with one focused workflow; retain the adapter, visible states and validation gates. Update the bilingual title and manifest identity consistently.

## Non-negotiable runtime rules

- Resolve the bridge lazily. Catch cross-origin parent access. Prefer the app's injected instance; use the supported parent path only in the intended CanEngine launch context, not as authorization.
- Wait a bounded time for injection, then show a useful host-missing state with Refresh. Never fabricate host success in browser preview.
- Distinguish method availability, configuration, permission, runtime readiness and actual task outcome.
- Inspect method-specific envelopes. A fulfilled Promise with `ok:false` is not success. A status query reporting a disabled feature is useful data, not a thrown exception.
- Route every user action through `try/catch/finally` and a single-flight guard. Clean up event subscriptions and polling on page disposal.
- Never automatically retry mutation/paid AI/send/install requests after timeout. Retain the unresolved action lock. Reconcile a late result with `recoverOutcome()` before another submission.
- Keep staged IDs, Phone Bridge file IDs, managed result refs, authorized paths and AI task IDs distinct. Preserve provenance; never infer an OS path from a browser filename.
- Use `openExternalURL()` for actions intended to open an external website; allow only validated HTTP(S) without embedded credentials. Internal prefill uses `browser.prefill` or `browser.openTarget`, not an external handoff. Do not guess `openURL` or `openExternal`.
- Native chooser cancellation is normal. Preserve cancellation without an error toast or false saved-file message.
- Prefer native file selection for large files. Limit browser-to-base64 transfers; do not inline large media.
- Prefer `assetURL` for package media and `{jobId,fileRef}` for result opening/exporting. Never retry a denied operation using a raw-path bypass.
- Run only manifest-declared packaged scripts. Never execute a selected user file, interpolate a shell command, or install packages in a click handler.

## Python and jobs

For long-lived local HTTP backends, follow `runtime.web` rules instead of spawning a Job per request. Include 1.8.0 support for stable per-app origin, isolated cookie container, deferred data import, sandboxed directories, uploads/downloads/SSE/WS and short-lived private JSON caching. Use ordinary HTTP Cache-Control, not guessed RPC APIs. Web cache diagnostics are available through `CanEngine.web.getStatus().cache`; this does not automatically persist database connections or business results.

When source protection is requested for a Python local website such as CanWeChat, read `references/python-compiled-packaging.md`. Add authoring-only `ceapp.build.json`, or generate `web-python --compile-python`. This configuration enables an optional capability: the matching CanEngine 1.8.0 packer still defaults to normal source packaging. Select Source protection packaging (Advanced) explicitly in the shared My/Canvas dialog, with the optional import password set inside that same dialog, or pass `ceapp-pack -mode python`. Only that mode checks/prepares compiler tools and runs the shared Mac/Windows pipeline: native Nuitka compilation, explicit asset selection, release-manifest rewriting, then existing signing. Build separately on the target OS/architecture; never claim cross-compilation. Export each foreign platform as .cebuild from the same source, import it in the shared dialog, then compile locally and merge/sign one CEAPP. Source fingerprint, app/version, platform, runtime contract, file digests, binary headers and common resources must match. .cebuild is a developer artifact, not signed or installable; accept it only from a trusted build environment. The final manifest maps runtime.web.nativeTargets to backend/<os>-<arch>/ entries, and installation extracts only the current target after full package signature verification. Unsupported platforms fail without fallback. Normal packaging keeps the manifest's platforms and can use one package across systems only when the code/dependencies are compatible. Keep source and versions intact, stop a protected build on failure without a source fallback, and verify the unpacked native app. This implementation requires `runtime.web` and empty commands; do not enable protection for the discrete-job `python` profile or remote-web. Compiled backends must use CANENGINE_HOST/PORT and CANENGINE_APP_DIR/APP_DATA_DIR rather than Python-only adapters or __file__ asset roots. Developer tools are prepared on demand and are not an installed app's runtime dependency. No new public Host Bridge API is provided, and compilation does not guarantee resistance to reverse engineering.

Read `references/runtime-and-jobs.md` before implementing any task.
The verified host blocks `runJob()` until execution ends. Subscribe to the full legacy `job:started` event BEFORE submission. Filter by appId/commandId and reject ambiguous ownership before cancellation. Do not await `runJob()` to obtain the first cancellable ID.
Use the supplied controller rather than writing a second lifecycle implementation.
Use managed output/result JSON and declared flags. Match runner CLI `-i`, repeated `--sequence` when needed, `-o`, `--result-json`. Check Python before execution; ask before installation. Never equate stop-waiting, cancel requested and terminal cancelled.

## AI, database and phone

Read the matching section of `references/bridge-recipes.md` and `references/phone-bridge.md`.
Keep provider credentials, routing and charging configuration in the host. Generate only after explicit user action and disclose external transmission/costs. Do not run paid generation as an automatic smoke test.
Use `ai.video.create` with the `ai.video.generate` permission. Treat video/3D as task lifecycles, not instant files.
Use the synchronous `data.local(collection)` factory and declare the collection schema. Shared access uses exact datasets and actions, not raw SQL or database paths.
Read a Phone Bridge `fileId` to Blob, then stage it before using it as a Python input. Treat QR/session values as secrets. Enforce sending confirmation in the app; do not rely on an ignored request flag.
Never auto-create notification features at startup or resurrect a deleted feature. A registration example is not a background business producer.

## Standard UI

These local UI requirements apply to the local HTML and packaged Web frontend. Preserve the design of an existing remote site. Remote websites render directly in the CanEngine main window's right pane with its left navigation intact. Use the native view's independent browser storage; no extra window, iframe wrapper, navigation button row or reserved toolbar height. Switching apps hides the page and preserves its state; host dialogs temporarily hide it and restore it afterward. Reload/browser/cache/data controls are in the running app entry's context menu. This is the remote mode default in the matching 1.8.0 build; do not invent an embedding flag or add app files/dependencies for this layout.

Read `references/standard-ui.md`. Adapt the selected design skill to the actual surface.
For this utility, use native local HTML/CSS/JS, consistent tokens, restrained typography, compact actions, light/dark themes and explicit responsive collapse. Do not force marketing-page hero rules onto a utility.
Keep labels above inputs; provide loading/empty/error/disabled/success/cancelled/unknown states.
Use textContent for filenames, AI output and diagnostics unless a sanitizer is deliberately provided.
Centralize `zh-CN`/`en-US` copy in `assets/ceapp-i18n.js`; follow host locale and unsubscribe cleanly.
Use system fonts. Never require a CDN for first paint.

## Mandatory validation gates

Run these scripts from the skill root in an environment supporting Python 3.10+ and Node 18+:

```bash
node --test tests/bridge.test.cjs
python tests/test_tools.py
python tests/test_prefill.py
python scripts/audit_contract.py assets
python scripts/validate_ceapp.py /path/to/generated-app --report /path/to/validation.json
```

For UI changes, run `tests/browser_smoke.py` on the full Lab with Playwright + Chromium installed. This runner inlines local files because some controlled browsers block navigation; it does NOT verify native asset routing. Test a generated business app's actual workflow separately. Never silently skip missing dependencies and mark PASS.
For the prefill template, also run `tests/prefill_browser_smoke.py --out /path/to/report` with Playwright/Chromium. It exercises the real local server and explicitly simulated bridge responses; the website/native gate remains separate. See `references/form-prefill.md` for research, negative cases and privacy checks.

Execute the produced Python script with a real fixture as well as syntax checking it. Test malformed/empty/Unicode input, cancel, unavailable runtime, permission denial, duplicate submit and negative envelopes. Extend tests when a new behavior is added.
For remote websites there is no Python job gate: test right-pane bounds on resize, switching apps without reloading, host dialog/menu layering, view close/reopen without closing the host, navigation, offline failure/retry, file chooser, downloads, actual site workflow, per-app storage, process restart, cache clear and data-clear confirmation. Use synthetic data when sending test forms. Cross-origin login and popup/opener flows need specific acceptance; current new-window links navigate in the same website view. Browser mocks cannot verify native profile isolation.

Read `references/testing-and-acceptance.md`. Mark each layer independently:
`PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `SIMULATED`.
The native gate must include installed CanEngine on each claimed OS, real file pick/open/export, runtime, shared permission behavior, relevant configured AI/device flows and package installation. Do not label browser mocks or absence of build logs as native success.
Fix failures before shipping or explicitly mark the unresolved gate. Do not claim that all future generated apps are guaranteed error-free.

## Deliver and explain

Provide the source location, short operation instructions, exact tests/results, pending native checks, and minimal relevant diagnostics. Use `references/packaging-and-signing.md` for the final client-side packaging flow.
For Canvas tasks, actually write the deliverable into that Canvas and read it back. A local ZIP alone is not Canvas completion.
Keep backups outside app package roots. Use `references/troubleshooting.md` to investigate failures without trying invented APIs.

## Reference map

- `references/source-baseline.md`: inspected implementation, versions, checksums, known limitations.
- `references/manifest-and-host-bridge.md`: public API contract, permissions and file types.
- `references/bridge-methods.json`: current source snapshot of public methods and factory members.
- `references/runtime-and-jobs.md`: blocking jobs, CLI/result contract and ownership.
- `references/python-compiled-packaging.md`: optional native Python build configuration, shared Mac/Windows pipeline, tool preparation and release checks.
- `references/bridge-recipes.md`: AI/data/system/notifications recipe guidance.
- `references/phone-bridge.md`: session, receive, import, send, expiry and permissions.
- `references/standard-ui.md`: reusable UI defaults and examples.
- `references/bilingual-framework.md`: locale and helper migration.
- `references/offline-runtime.md`: local startup and dependency boundaries.
- `references/web-app-modes.md`: mode choice, remote manifest/storage and verified 1.8.0 creation features.
- `references/remote-web-authorization.md`: protected remote declarations, single-PHP entry convention, license/session behavior and public/private boundaries.
- `references/local-web-runtime-1.8.0.md`: complete 1.8.0 local Web declarations, import/cache/download/Canvas limits and lifecycle.
- `references/form-prefill.md`: website-to-CEAPP workflow, 1.8.0 public browser JSON contract, field research, privacy, template and native gates.
- `references/demo-catalog.md`: complete projects and extension examples.
- `references/testing-and-acceptance.md`: evidence levels and native checklist.
- `references/troubleshooting.md`: symptom-to-contract checks.
- `references/packaging-and-signing.md`: clean source and authorized signing.
