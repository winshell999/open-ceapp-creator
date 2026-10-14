# Current user-authorized version · 1.8.0 · 2026-10-10

The user explicitly pins CanEngine, this skill and its CEAPP templates to 1.8.0. EngineVersion, Wails productVersion, frontend package metadata, browser profile minimums, every packaged template’s app/minimum version and the generator defaults now agree. Feature implementation does not authorize changing host/app/minimum versions; preserve them until the user supplies a new value. Use a matching implementation, not a version-string assumption.

The implementation and prior MDAC checks remain usable evidence. The historical sections below retain their original temporary/release numbering and hashes; they are not current version declarations or proof of native 1.8.0 acceptance. Current source/version/build checks are recorded in VERSION_1_8_0_VALIDATION_REPORT.md and VERSION_1_8_0_SOURCE_SHA256.json under ../reports/.

## Protected remote website declaration · 1.8.0 · 2026-10-14

Inspected the matching CanEngine 1.8.0 remote manifest, private launch-ticket client, native authorization lifecycle and authorization-center model/service. `runtime.remoteWeb.authorization: "canengine"` opts into an online one-time-ticket handshake; remote documents still receive no Host Bridge. The generator and validator now support this declaration without changing version defaults. Website registration, formal-license/device checks and server-side verification remain separate requirements. A single PHP entry may handle the fixed handshake through PATH_INFO when the website server supports it.

Public source hashes use repository-relative names in `../reports/REMOTE_WEB_AUTH_SOURCE_SHA256.json`. Creator regression results and evidence boundaries are in `../reports/REMOTE_WEB_AUTH_VALIDATION_REPORT.md`. No live website address, secret, personal filesystem path, cookie, authorization payload or screenshot is included in these records.

## Historical evidence before the explicit version correction

# Controlled generic browser prefill · 2026-10-10

Inspected in the matching CanEngine 1.7.11 source: public runtime.web CanEngine.browser.prefill/openTarget/getStatus/close, engine browser manifest governance, desktop owner/session handling, native WKWebView/WebView2 and strict DOM prefill adapter. Minimum 1.7.11 for form-prefill-v1 and browser.form.prefill; the historical 1.7.10 MDAC open/fill adapter remains compatible. This adds a controlled browser surface to local Web only; remote websites still receive no Host Bridge. Existing 1.7.9 Web and Python packaging sections below retain their historical baselines.

Fixed signed HTTPS targets, exact-origin navigation and full-page/document binding; strict JSON has bounded fields, types, selectors, dependency DAG and explicit input/change/blur events. No arbitrary evaluate/DOM-read/script, CAPTCHA/consent/submission API. Values pass through local authenticated bridge memory rather than URL/logs/status. Defaults do not emit events; site AJAX semantics require research. See [form-prefill.md](form-prefill.md). Source hashes and evidence boundaries: ../reports/FORM_PREFILL_SOURCE_SHA256.json.

Actual macOS 1.7.11 CanEngine filled MDAC with synthetic data 22/22 and verified manual editing, return preservation, refresh reset, protected-field rejection and owner close. Host full Go regressions, 102 frontend tests and macOS/Windows compilation passed, recorded in host docs/form-prefill-acceptance/. Windows native NOT_RUN. These results do not establish this skill's new starter or any other site's native acceptance; every generated app keeps a separate native gate.

# Native artifact merging and shared password UI · 2026-10-07

The matching CanEngine 1.7.9 build now supports local compilation plus imported .cebuild artifacts from separately built target platforms, merged and signed as one CEAPP. The runtime manifest uses nativeTargets; package installation verifies the whole container before extracting only the current OS/CPU backend and common resources. UI labels are Source protection packaging / Advanced, environment readiness is green, Install build environment replaces Prepare, and My/Canvas both set import password inside the shared dialog. Source fingerprints are consistency metadata, not build-source attestation. No new public Host Bridge API or host/app version bump. CanWeChat remains Mac arm64 pending business dependency migration. Evidence and exact pending native gates are in reports/NATIVE_MULTI_VALIDATION_REPORT.md, source hashes in reports/NATIVE_MULTI_SOURCE_SHA256.json and host docs/ceapp-multiplatform-acceptance/.

# Explicit packaging modes and shared UI · 2026-10-07

The matching CanEngine 1.7.9 build now defaults to normal packaging, even with ceapp.build.json. My and Canvas share frontend/src/ceappPackaging.jsx and submit explicit mode/password choices through CEAppSignerPackageProject. Only mode python invokes compilation; ceapp-pack requires -mode python for a protected build. Optional invalid build metadata does not block normal source packaging. Both modes verify the completed container before committing it. Current source hashes and acceptance states are in reports/PACK_MODE_SOURCE_SHA256.json and reports/PACK_MODE_VALIDATION_REPORT.md. UI/backend evidence is recorded in the host's docs/ceapp-packaging-acceptance; the earlier native compiler evidence below remains separate. Existing host/app versions are preserved.

## Python compiled packaging addition · 2026-10-07

Inspected in the current CanEngine 1.7.9 source: internal/engine/ceapp_build.go/ceapp_build_tools.go, ceapp_container.go/ceapp_signer.go; internal/desktopapp/app_ceapp_build.go and packaging/Canvas methods in app.go; cmd/ceapp-build/cmd/ceapp-pack; frontend/src/ceappBuild.jsx/ceappBuildUtils.mjs and signer/Canvas integration. The host and CanWeChat manifest versions remain 1.7.9 and 1.0.9. Source hashes and acceptance states are recorded in reports/PYTHON_BUILD_SOURCE_SHA256.json and reports/PYTHON_BUILD_VALIDATION_REPORT.md. These additions do not extend the public CEAPP Host Bridge registry.

One shared Go pipeline compiles Python local websites through Nuitka4.2.2, selects explicit native/assets output, rewrites only the staged runtime manifest and uses existing signing. Mac and Windows packages must be built separately on their OS/architecture. Developer tools are downloaded on demand, with Windows native dependency warmup; they are not bundled into the host installer. Authoring config generation/validation uses web-python --compile-python.

Mac arm64 CanWeChat and the generated stdlib Web template were actually compiled. Their signed containers were verified/extracted with one-off synthetic keys and launched through the real host sandbox. CanWeChat read an encrypted synthetic SQLite shard and decoded its latest zstd message; the template preserved a synthetic note and stable origin through backend reopen. The unpacked releases have no business .py/.pyc. These tests do not use or authorize real WeChat data or trusted publisher identities. This Python3.14.7 build requires macOS15.0; host version alone cannot promise an older target OS. CanWeChat currently remains Mac arm64 because its existing native libraries/manifest are Mac-specific.

Windows amd64 host compilation and cross-platform release-contract tests pass; actual Windows tool preparation, Python native compilation, signature/install and end-user runtime gates remain NOT_RUN. The new React panel has simulated-browser locale/layout/cancel/remount coverage; production Wails sign/save/install remains a separate native gate.

# Source baseline · 2026-10-06

Current mode additions were inspected in the authorized local CanEngine repository. Both local and remote Web modes are implemented in the current 1.7.9 source; preserve that host version and use a matching build. An older binary carrying the same version number does not gain these additions from a manifest change. The historical static Bridge evidence below remains separate.

- 1.7.9: runtime.web manifest and generator, stable origin, cookie containers, app data/temporary directories, declarative/deferred setup, restricted Web Bridge, sandbox lifecycle, native download, Canvas WeChat import and private JSON caching. Full contract: local-web-runtime-1.8.0.md.
- 1.7.9: runtime.remoteWeb, manifest-only container anchor, native WKWebView/WebView2 embedded in the main window's right pane, per-app persistent or ephemeral storage, navigation origins and running-app context menu controls. Switching apps retains the page; dialogs temporarily hide it. No separate website window, added toolbar, embedding manifest flag or extra app package. Remote pages receive no Host Bridge.

Inspected files include internal/engine/types.go, manifest.go, web_manifest.go, remote_web_manifest.go, package_manager.go, web_service.go, web_cache.go; internal/desktopapp/app.go/app_web.go/app_remote_web.go; internal/remoteweb; frontend/src/main.jsx/webAppBridge.mjs/remoteWebSurface.mjs; main.go; cmd/ceapp-web and cmd/ceapp-remote; docs/ceapp-web-runtime.md/ceapp-remote-web.md. Current source hashes are in reports/WEB_SOURCE_SHA256.json.

Full Go regression and frontend 68 tests passed. A signed manifest-only package roundtrip passed on EngineVersion 1.7.9. The macOS arm64 Host builds with both bundle versions 1.7.9. The real new Host launched the already installed and authorized EA 1.0.0 app, verified right-pane layout, native Excel selection and analysis, preserved results across page switches and window zoom, and tested context menu/notification layering and native data-clear cancellation. A developer preview with the same native implementation revalidated persistent storage on refresh/app reopen/process restart, appId isolation, ephemeral discard, cache clearing and no Host Bridge. Fresh package installation through production UI, native language switching and Windows runtime remain separate pending gates. Windows amd64 compiles. Record: reports/WEB_VALIDATION_REPORT.md.

No production account, signing identity or security policy was bypassed. No test result establishes arbitrary website compatibility or offline availability. Current remote new-window links navigate in the same website view; advanced OAuth popup/device flows need specific testing.

# Historical static Bridge baseline · 1.7.3

Inspected on 2026-09-26 using the authorized CanEngine Canvas connector. This is a code/handoff snapshot, not proof that every user's installed build exposes every method.

## Source priority

1. The installed app's public injected bridge and observed host version.
2. Matching `frontend/src/main.jsx` public bridge and backing Go request/response types.
3. Version handoff and repository `Apps/demo`.
4. This skill snapshot.

Do not equate source version 1.7.3, packaged release availability, remote publishing and completed native acceptance. The version README explicitly distinguishes these.

## Inspected files

- `version/v1.7.3/README.md`
- `version/v1.7.3/01_Recent_Changes_Handoff.md`
- `version/v1.6.6/02_Architecture_API_Data.md`
- `version/v1.6.6/04_Phone_Bridge_Device_Bridge_Handoff.md`
- `Apps/demo/app.json`, `Apps/demo/app.js`, `Apps/demo/README.md`
- `Apps/demo/scripts/demo_job.py`, `Apps/demo/data/localdb.schema.json`
- `frontend/src/main.jsx`, especially the public bridge around lines 2800-3115
- `internal/desktopapp/app.go`, including JobsRun and OpenExternalURL
- `internal/engine/runner.go`, including Run, buildCommandArgs and job events

## SHA-256 evidence

| Repository-relative file | SHA-256 |
|---|---|
| frontend/src/main.jsx | e7d335829ae3dc32e0c618cb41cc8b94f855aadacca4650373012a3bdc0dbfa8 |
| internal/engine/runner.go | 466017c6f8346fccbec655dd127096b2c6ed0cda75fe159affc0135dac65fdba |
| Apps/demo/scripts/demo_job.py | 222baee07e735d1f59c46d8dfaa88496192cdeaa5758aa4089bb31932ad26d18 |
| Apps/demo/data/localdb.schema.json | a40a0dab8ac3e8db0cae4189ee292aa9e6cdf16fb4a1be81bb6591b527457e3f |
| version/v1.7.3/01_Recent_Changes_Handoff.md | eb32a41a9b85ee36e432e74eac2d36124887b7e28627fc3d93a92071a2337ec4 |

## Confirmed implementation details

- `runJob()` waits for the process to exit; subscribe before starting.
- `job:started` includes full JobInfo. `job.started` only includes type and jobId.
- `openExternalURL()` is exposed. `openURL()` is not in this snapshot.
- `ai.video.create()` is the method; `ai.video.generate` is the feature/permission.
- `data.local` and `data.dataset` are synchronous factories returning async methods.
- Phone `readFile` resolves to Blob; `sendToPhone` consumes fileIds. Its JS wrapper does not consume `requireUserConfirm`, so the app must confirm before calling.
- Runtimes, file permissions, AI sessions and device availability can still block a correctly shaped call.
- The old demo declares example shared resource IDs. The new starter deliberately declares none.

## Boundaries not changed by this refactor

During the 2026-09-26 refactor the host repository was read, not patched. The static adapter cannot repair a missing host method, disconnected phone, failed runtime installer, provider error, or OS-specific WebView bug.
No universally reliable cross-window job correlation token exists in the inspected `runJob` contract. The adapter blocks existing matching jobs and refuses ambiguous cancellation; it cannot create backend idempotency or prove exactly-once execution across app windows/restarts.
The in-memory unknown-outcome guard protects the current view. After host/app restart, inspect the host history before retrying a charged or side-effecting action.
A newer bridge needs a refreshed registry and regression tests, not a permissive guess-based fallback.
