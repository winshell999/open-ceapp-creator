---
name: open-ceapp-creator
description: Create, debug or refactor CanEngine CEAPP source projects with verified public host-bridge contracts, a tested adapter, runnable demos, least-privilege manifests and local UI assets. Use for file pick/open/export, Python jobs, runtime readiness, safe website opening, AI, local/shared data, Phone Bridge, notifications, clipboard, print, locale and diagnostics. Also use when a CEAPP works in a browser but fails inside CanEngine, or when packaging reports missing files or unsupported capabilities. Produce source, validation evidence and a host-acceptance checklist, not invented APIs or trusted signatures.
---

# Open CEAPP Creator

Generate from verified contracts and tested components, not from remembered API names.
Treat this skill as an executable generation workflow. Do not deliver a plan alone when asked for an app.

## Deliverables

Return a clean CEAPP source directory, a validation report, and a completed/pending native acceptance record.
When updating this skill itself, return the complete `skill.zip`.
Keep the app version independent of the host version. Do not manufacture official/KOL signatures.

## Start with evidence

1. With a supplied Canvas ID, first call `get_work_context_for_canvas` with that exact ID, confirm the returned ID, then use the same explicit ID on every Canvas operation.
2. Read the selected UI skill and existing project entry/manifest/dependencies before editing. Back up changed files, preserve unrelated files and signer/license boundaries.
3. Read `references/source-baseline.md` and `references/manifest-and-host-bridge.md`.
4. Locate the user's handoff/current source through authorized Canvas tools. Resolve any disagreement against the public `window.CanEngine` implementation and the relevant Go types/runner. Do not use private source paths as shipped configuration.
5. Record source version/date/hash and the methods actually consumed. If source is unavailable, use this snapshot conservatively and state that it was not refreshed. Do not invent methods to fill a gap.
6. Distinguish the authoring MCP tools from the CEAPP runtime. A connector exposed to the AI is not automatically an app bridge. Never call arbitrary Wails/Go internals from CEAPP code.

## Select a narrow profile

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

```bash
python scripts/create_ceapp.py --app-id my-file-tool --name "My File Tool" --profile python --output /path/to/new-project
python scripts/validate_ceapp.py /path/to/new-project --report /path/to/validation.json
```

For shared data, pass the real `--dataset` / `--action` IDs; the generator synchronizes manifest and configuration. Never seed a required imaginary dataset. Existing output directories are intentionally refused.

## Build by reusing components

Copy the generated project, then change business logic, message tables and the relevant panels.
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
- Use `openExternalURL()` for websites; allow only validated HTTP(S) without embedded credentials. Do not guess `openURL` or `openExternal`.
- Native chooser cancellation is normal. Preserve cancellation without an error toast or false saved-file message.
- Prefer native file selection for large files. Limit browser-to-base64 transfers; do not inline large media.
- Prefer `assetURL` for package media and `{jobId,fileRef}` for result opening/exporting. Never retry a denied operation using a raw-path bypass.
- Run only manifest-declared packaged scripts. Never execute a selected user file, interpolate a shell command, or install packages in a click handler.

## Python and jobs

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
python scripts/audit_contract.py assets
python scripts/validate_ceapp.py /path/to/generated-app --report /path/to/validation.json
```

For UI changes, run `tests/browser_smoke.py` on the full Lab with Playwright + Chromium installed. This runner inlines local files because some controlled browsers block navigation; it does NOT verify native asset routing. Test a generated business app's actual workflow separately. Never silently skip missing dependencies and mark PASS.

Execute the produced Python script with a real fixture as well as syntax checking it. Test malformed/empty/Unicode input, cancel, unavailable runtime, permission denial, duplicate submit and negative envelopes. Extend tests when a new behavior is added.

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
- `references/bridge-recipes.md`: AI/data/system/notifications recipe guidance.
- `references/phone-bridge.md`: session, receive, import, send, expiry and permissions.
- `references/standard-ui.md`: reusable UI defaults and examples.
- `references/bilingual-framework.md`: locale and helper migration.
- `references/offline-runtime.md`: local startup and dependency boundaries.
- `references/demo-catalog.md`: complete projects and extension examples.
- `references/testing-and-acceptance.md`: evidence levels and native checklist.
- `references/troubleshooting.md`: symptom-to-contract checks.
- `references/packaging-and-signing.md`: clean source and authorized signing.
