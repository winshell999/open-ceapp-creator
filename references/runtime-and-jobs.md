# Runtimes, Python and managed jobs

## State sequence

idle -> checking runtime -> submitting -> running -> success/failed/cancelled.
An elapsed waiting deadline produces outcome-unknown, not success and not cancellation.
Keep the operation guarded until a terminal host state or reconciled late response is observed.

## Blocking contract

In the inspected host, JobsRun delegates to Runner.Run. The runner invokes cmd.Start, emits a full `job:started` JobInfo, drains logs, waits with cmd.Wait, finalizes result JSON and only then resolves runJob.
Therefore `const job = await runJob(...); enableCancel(job.id)` enables Cancel too late.
The supplied JobController installs listeners before submitting and verifies appId/commandId. It ignores foreign apps. `job.started` alone is insufficient because it omits those ownership fields.
Before cancel, list jobs and require exactly one active matching command with the expected ID. If multiple windows start the same command, refuse ambiguous cancellation rather than stop someone else's task. Do not claim cross-process exactly-once semantics.

## Event map

| Legacy event | Full/partial value | Dotted event |
|---|---|---|
| job:started | Full JobInfo with appId, commandId, id | job.started has type/jobId only |
| job:log | id, stream, line | job.stdout / job.stderr have jobId, message |
| job:completed | Full JobInfo | job.completed has jobId, result |
| job:failed | Full JobInfo | job.failed has jobId, error |
| job:cancelled | Full JobInfo | job.cancelled has jobId |
| none | ResultFile available | job.file has jobId, file |

Use one event family for updates to avoid duplicates. The Lab uses full legacy lifecycle events and a separate log-read action.
Clean up subscriptions on terminal state/disposal. Navigation away must not silently cancel a running user job.

## Runtime installation

`requireRuntime('python-runtime')` is a readiness check returning an ok envelope. It is not a guarantee of installation.
Only an explicit user-confirmed action calls installRuntime, then recheck readiness. A UI should remain usable when an optional runtime is missing. Host-managed runtime installation can fail due to network, permissions or platform support.
Keep runtime and script package dependencies separate. This starter uses Python standard library only. For extra packages, use a documented managed dependency strategy and verify its imports before enabling a task; do not invoke pip from the CEAPP.

## Actual runner CLI

The runner copies staged inputFileIds into its per-job input directory and appends:

```text
<baseArgs> -i <first materialized input> -o <outputDir> <request args> --result-json <resultJson>
```

For request mode `sequence`, it instead appends one `--sequence <path>` per input.
Do not pass your own -i/-o/--result-json through args or duplicate runner-owned arguments.
Use explicit allowedFlags in app.json. The demo allows only `--sleep` and validates a 0-10 second range.

## Script result contract

The bundled script writes:

```json
{"ok":true,"status":"success","files":[{"name":"inspection.json","path":"<host output path>","type":"file","mime":"application/json","size":100}],"warnings":[],"durationMs":12}
```

Use real absolute output paths assigned by the host, not those illustrative values. The JSON's files list must match actual files on disk. Write atomically via a sibling temporary file and os.replace. On a processing failure, write ok:false/status:failed/error/files:[] where possible and exit nonzero. If the output directory itself is unwritable, stderr/nonzero exit remain authoritative.
Do not forge fileRef; the host owns managed references.

## Demonstration operation

Files > Sample file -> Python tasks > Inspect file -> choose inspection.json -> Open / Export.
Cancellable task adds a five-second delay; Cancel uses the verified pre-return job ID. After cancel request, refresh and show the real terminal state.
The script hashes input, inspects text/CSV/JSON, copies it and writes inspection.json. It does not execute user input. UTF-8/BOM and filenames with spaces/non-ASCII are tested. Text parsing is capped at 16 MiB; generic binary hashing streams in 1 MiB blocks.

## Timeout reconciliation

The generic mutation adapter leaves timed-out side effects guarded even after a late response arrives. Diagnostics shows pending/unknown actions. Its Read action retrieves an already returned late outcome; for media creation the task ID is restored. No late result is logged with secrets.
For Python the controller tracks terminal events and the original Promise. After reconnect/reload, inspect host history before a repeat because an in-memory UI lock cannot enforce backend idempotency.
