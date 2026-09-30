# Manifest and public host bridge

## Navigation

Manifest and permissions; typed file identities; calls and envelopes; API groups; safe compatibility.
The machine-readable method inventory is `bridge-methods.json`. The full runnable manifest is `../assets/starter/app.json`.

## Manifest invariants

Use schemaVersion 1, a stable lowercase appId, independent app version, package-relative entry/icon, bilingual metadata, flat permission strings and nonempty commands.
The baseline targets CanEngine 1.7.3. Runtime requirement optionality is `optional: true`, not `required: false`.
A purely visual app uses an inert `echo` command only to satisfy the packer; never wire it to a button or claim that it performs a task.
For Python, declare executable `python3`, packaged script in baseArgs, only accepted allowedFlags, and a python-runtime requirement. Keep Python optional for a Lab so the rest of its UI is usable, but check it before every task.

## Identity types must not be interchanged

| Value | Origin | Valid use |
|---|---|---|
| Browser File/Blob | Picker, paste, DOM drop | Bounded stageFile dataBase64, browser preview |
| StagedFile.id | chooseFile / stageFile | runJob inputFileIds |
| StagedFile.path | Host staging result | AI temp-file input or authorized file helpers |
| ChosenDirectory.id | chooseDirectory | exportFile targetDirectoryId |
| JobInfo.id | runJob or verified full event | getJob/getJobLogs/cancelJob |
| ResultFile.fileRef | That job's files | openFile/exportFile/revealFile with jobId |
| Phone file.fileId | Phone Bridge receive/add | phone readFile/sendToPhone only |
| AI task.taskId | video/3D creation | Matching getTask/cancelTask only |

Never derive an OS path from an HTML file input. Never accept a result reference from a different job simply because its name matches.

## Request/response essentials

```js
await host.chooseFile({appId, title, accept:['image/*']}); // StagedFile or null
await host.chooseFiles({appId}); // StagedFile[]; cancel gives []
await host.stageFile({appId, name, dataBase64, mime}); // StagedFile
await host.stageFile({appId, sourcePath}); // path from native authorized drop only
await host.runJob({appId,commandId:'inspect',inputFileIds:[staged.id],args:[]});
await host.openFile({jobId:job.id,fileRef:file.fileRef});
await host.exportFile({jobId:job.id,fileRef:file.fileRef,suggestedName:file.name,targetDirectoryId:directory.id});
await host.openExternalURL('https://example.com');
```

StagedFile contains id/appId/name/path/size and optional mime/sha256/createdAt.
ChosenDirectory contains id/path/name/writable/createdAt.
JobInfo contains id/appId/commandId/ok/status/files and optional error/exitCode/stdout/stderr/logs/timing.
ResultFile contains name/path/type/mime/size and optional fileRef.
No app-generated fake fileRef is permitted. Use legacy sourcePath only when the actual returned file lacks fileRef, not when a fileRef request was denied.

## Calls and failure envelopes

Use `client.call()` for read-only inspection and `client.mutate()` for external effects. The wrappers preserve the owning object as `this` and normalize thrown errors.
Each domain must still validate its response. `requireRuntime` with ok:false is a blocked workflow. `runJob` with ok:false or failed status is failure even though its Promise resolved. A cancelled chooser is not failure. A disabled bridge reported by getStatus is state data.
Some methods legitimately resolve `undefined`/null after an acknowledged native operation. Do not require `{ok:true}` universally. Opening a print/save dialog or accepting an AI task is not proof of completed printing/saving/generation.

## Permission map

AI: exact feature string in both capabilities.ai.features and permissions; use required:false for optional enhancements.
Data: data.read/data.write for app-private collections; data.schema/data.action when used. Shared datasets/actions must be declared by exact ID in both manifest and configuration.
Phone: phoneBridge.openPanel/createSession/receiveFiles/readFiles/addFiles/sendToPhone as individually needed.
Notification: notification.send for immediate notification; notification.schedule for persisted features. The basic demo intentionally does not ask for schedule.
File/runtime/clipboard/URL methods: do not invent permission strings. Inspect the host's actual governance.

## API groups

- Host: getCapabilities, hasCapability, getHostVersion.
- Runtime: getRuntimeStatus, requireRuntime; older list/check/install/app/environment helpers remain opt-in.
- Input: chooser, stage, native drop, bounded File/Blob.
- Output: managed result references, legacy path helpers only with authorized provenance.
- Assets: assetURL for display, assetDataURL only for small inline/copy use.
- Jobs: full legacy event correlation, terminal result inspection and cancellation reconciliation.
- AI: text/vision/image responses; video/3D task IDs and separate polling.
- Data: factory-produced collection/dataset methods; action API for configured operations.
- Phone: host-owned sessions/workbench, read Blob, explicit send.
- System: clipboard, print, external URL, diagnostics and locale.

## Compatibility policy

Prefer the modern method when present. Fall back only on absence, never after permission denial.
Keep browser preview explicitly labeled; do not return fake host output.
When the host is present but an asset or method fails, surface that failure. Do not quietly use a browser alternative that hides a broken installed app.
Never access window.go/window.runtime, embedded credentials, internal localhost APIs, arbitrary shell, raw shared SQL, or AI connector routing internals.
