# Test gates and native acceptance

## Controlled website prefill · 1.8.0

Read [form-prefill.md](form-prefill.md) and require value-free evidence from the actual target DOM before claiming a ready mapping. Run `tests/test_prefill.py` and the real-local-server `tests/prefill_browser_smoke.py`; record simulated Host Bridge as SIMULATED. Test the signed app in actual CanEngine, separately per OS: fixed authorized page opens in the right native pane, each field reads back correctly, manual edit persists on return, reload clears stale results, changed/ambiguous/protected controls fail safely, unknown outcomes lock repeat actions, undeclared targets/redirects fail, and closing the owner closes its session. Verify values absent from URL/log/status/unnecessary files. Keep CAPTCHA, consent and final submit untouched. Preserve existing SQLite schema/data. Historical macOS MDAC 22/22 is existing host evidence, not native acceptance of every new generated app; Windows compilation is not Windows runtime acceptance.

## Evidence labels

PASS: actually executed successfully at the stated layer.
FAIL: executed and failed.
BLOCKED: prerequisites prevent execution, with a recorded reason.
NOT_RUN: not attempted.
SIMULATED: synthetic host/provider/device behavior; never relabel as native PASS.

## Automated gates

1. Skill package: valid frontmatter, agent metadata, complete files, no private keys/fonts, under 25 MiB.
2. Contract inventory: audit literal bridge call names. Dynamic method prefixes and request/response types still need dedicated tests/review.
3. CEAPP structure: app identity, manifest permissions, entry/icon assets, declarations, schema, allowed flags, no CDN/bypass, JS/Python syntax.
4. Real script fixtures: UTF-8/non-ASCII filenames, empty/malformed input, sequence, binary/hash, output JSON/files, refusal to overwrite input.
5. Adapter fixtures: absent/delayed/cross-origin host, permission denial without bypass, null chooser, resolved failure, mutation lock, timeout/late result, data factories, media shapes, job ownership/cancel, cleanup.
6. UI: 1440/768/390 px, both themes, all panels, local file preview, keyboard/focus inspection and error state.
7. Simulated integration: staged input -> job -> results; explicit AI; CRUD; phone; notification; clipboard/print/URL; diagnostics. Fixture execution does not touch these real services.

Commands:

```bash
node --test tests/bridge.test.cjs
python tests/test_tools.py
python scripts/audit_contract.py assets
python scripts/validate_ceapp.py assets/starter
python tests/browser_smoke.py --app assets/starter --out /path/to/browser-results
```

Browser runner dependencies: Python Playwright plus an installed Chromium. Pass --browser for a custom executable. It uses locally inlined HTML/CSS/JS to avoid controlled-browser navigation restrictions; package asset routing, file:// and WebView launch are NOT covered by that renderer. The app itself has no Playwright/Node development dependency.

## Required installed-host checklist

Complete for each supported OS/build (macOS WKWebView and Windows WebView2 separately):

| Case | Expected evidence | Initial state |
|---|---|---|
| Package/sign/install | Client validates, signature label correct, installed app launches | NOT_RUN |
| Host identity | Actual version/platform/capabilities recorded without secrets | NOT_RUN |
| Offline shell | No network startup dependency after install | NOT_RUN |
| Native file choose/cancel | File staged correctly; cancellation no error | NOT_RUN |
| Native drop/paste | Exactly one ingestion per input, no duplicate processing | NOT_RUN |
| Unicode/space path | Processing and export succeed | NOT_RUN |
| File open/reveal/export | Real system apps/dialogs, correct saved bytes | NOT_RUN |
| Python missing | Clear blocked state, no execution | NOT_RUN |
| Runtime install | Explicit approval, result rechecked | NOT_RUN |
| Python success/failure | Real result JSON/files, actual error surfaced | NOT_RUN |
| Slow task/cancel | Verified ID available before completion; terminal cancellation confirmed | NOT_RUN |
| Repeated click | One submitted operation, no duplicate files/charge | NOT_RUN |
| Two app windows | Ambiguous ownership never cancels the wrong job | NOT_RUN |
| External website | Host opens validated address; unsafe schemes rejected | NOT_RUN |
| AI disabled/denied | Useful explanation, no provider bypass | NOT_RUN |
| Configured AI | Authorized paid test per required modality only | NOT_RUN |
| AI timeout/late result | No auto resend; task/result reconciled | NOT_RUN |
| Local SQLite CRUD | Data persists through app restart | NOT_RUN |
| Shared dataset/action | Real declared IDs, grant/deny/revoke, schema mismatch | NOT_RUN |
| Phone receive | Real phone -> callback -> Blob -> staged input | NOT_RUN |
| Phone reverse send | Explicitly confirmed, real phone receives correct bytes | NOT_RUN |
| Phone expiry/disconnect | Clear failure, host-panel renewal, no token leak | NOT_RUN |
| Notification governance | Explicit registration/deletion if included, no resurrection | NOT_RUN |
| Clipboard | Correct text/image/file type in a real target app | NOT_RUN |
| Print | Native dialog and actual output checked separately | NOT_RUN |
| Locale/theme | Host change propagates; app unsubscribes when closed | NOT_RUN |
| Packaged media | Image/audio/video URL resolution after install | NOT_RUN |
| Diagnostics | Sensitive data reviewed before export/share | NOT_RUN |

Record who ran each case, exact installed build, timestamp, outcome and minimal evidence. Do not use an empty error log as proof that all cases passed.

## Release statement

Prefer: "Structure, fixture tests and browser UI passed; native file dialogs/AI/phone on these platforms remain NOT_RUN."
Never: "All bridges passed" or "future generated apps cannot fail" based only on mocks or static inspection.
# Web mode acceptance additions

For runtime.web (1.8.0), verify a single persistent backend, constant origin after reopen, data persistence, runtime/sandbox unavailable states, external read/write directory bounds, deferred setup import/cancel and HTTP upload/download/Range/SSE/WS as applicable. Check private JSON cache hits, write/account-switch invalidation and no-store bypass without logging private URLs or response bodies. The Python standalone fixture is not native sandbox acceptance.

For runtime.remoteWeb (1.8.0), verify the first-party native view occupies the main window's right pane without a separate window or toolbar. Resize it, switch away/back without reloading, and open/close host dialogs and the app context menu; the website must not cover these controls or remain visible over another page. Closing the app/view must not close the host. Verify app-private storage on refresh, app reopen and process restart; a second appId on the same origin must start with separate data. Test ephemeral close/reopen, declared/undeclared navigation, TLS errors, offline/retry, actual file input/download and site login flows. Cache-only clearing must preserve cookies/DOM; full data clearing must ask natively and sign out. No Host Bridge should exist in the remote document. Validate popup/opener and device features individually.

For `authorization: "canengine"`, separately verify formal-license launch, trial/expired/revoked/device refusal, no-cookie page/API/static refusal, single-use/expired/cross-app tickets, old-cookie invalidation after failed handshake, fixed session expiry and online close/reopen. Switching and normal refresh should reuse the session. A declaration validation PASS is not a website access-control or native handshake PASS. Test the single-PHP PATH_INFO route only on a server that actually supports it, and verify no-store responses. Check the delivered signed metadata/payload minimum 1.8.0. Keep tokens, keys, tickets, sessions, real site identities and private paths out of public evidence; record macOS and Windows native outcomes independently. The full protocol boundaries are in [remote-web-authorization.md](remote-web-authorization.md).

Record macOS 14+ and Windows/WebView2 results separately. Mac preview success does not prove Windows support or production Host installation. Ordinary site caching does not prove offline startup or business-result persistence. New-window links currently navigate in the same window, so do not claim general OAuth popup compatibility.

## Python native packaging additions

For `ceapp.build.json`, distinguish authoring-config PASS from native compiler PASS. Verify actual Mac/Windows outputs separately, native executable architecture, packaged libraries, preserved versions/appId, no business .py/.pyc or build metadata, retained runtime permissions and unchanged source. Run the unpacked compiled backend and inspect health/frontend plus synthetic business fixtures. Validate signer/container extraction and installation separately; a temporary test key is not an official identity. Check missing Python.h/compiler/Nuitka, rejected unsupported targets, source leaks, duplicate submission, operation-owned cancellation, page-switch progress recovery, cleanup and preservation of a previous output after failure. No compilation fallback may expose source.
