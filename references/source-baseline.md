# Verified source baseline

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

The CanEngine host repository was read, not patched. The new skill cannot repair a missing host method, disconnected phone, failed runtime installer, provider error, or OS-specific WebView bug.
No universally reliable cross-window job correlation token exists in the inspected `runJob` contract. The adapter blocks existing matching jobs and refuses ambiguous cancellation; it cannot create backend idempotency or prove exactly-once execution across app windows/restarts.
The in-memory unknown-outcome guard protects the current view. After host/app restart, inspect the host history before retrying a charged or side-effecting action.
A newer bridge needs a refreshed registry and regression tests, not a permissive guess-based fallback.
