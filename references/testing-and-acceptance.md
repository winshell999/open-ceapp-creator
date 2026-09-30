# Test gates and native acceptance

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
