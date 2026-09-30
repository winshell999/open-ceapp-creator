# Bridge recipes

## AI

Keep configuration and secrets in the host. Always expose missing/disabled/denied states. Send nothing automatically at startup. Explicit actions may incur provider costs.

Text: `ai.text.generate({messages:[{role:'user',content}],maxTokens:400})`, consume response.text.
Vision: stage an image then `ai.vision.analyze({prompt,images:[{type:'temp-file',path:staged.path}],maxTokens:400})`.
Image: `ai.image.generate({prompt,size:'1024x1024',count:1})`; inspect the returned provider-supported result rather than assuming a remote URL is always present.
Video: `ai.video.create({prompt,inputImage:{type:'temp-file',path},durationSeconds:4,ratio:'16:9',quality:'preview'})`.
3D: `ai.model3d.generate({prompt,inputImages:[{type:'temp-file',path}],outputFormat:'glb',quality:'preview'})`.
Media request parameters above follow the inspected official demo; provider support may differ. Report unsupported format/duration as a configuration/task error rather than silently switching providers.

For video/3D retain taskId, inspect status, poll with a deadline, offer explicit cancel and never equate stop watching with stopped generation. Do not resume paid creation after an ambiguous timeout. Recover the late create result first. Open only an actual successful returned result.localPath. Other provider result shapes need explicit source-backed adaptation.
The Lab displays raw-safe returned metadata and text. It does not claim a universal 3D renderer or video transcoder.

## Data

`const store = host.data.local('bridge_lab_notes')` returns a synchronous wrapper.
Use store.put({id,text,updatedAt}), store.get(id), store.find({limit:20}), store.delete(id).
The private collection is declared in data/localdb.schema.json. This is not direct SQL and not unrestricted filesystem access.

For shared data, use a generated data/full profile with actual `--dataset`/`--action` values. Read via host.data.dataset(id).find({limit:20}); schema via host.data.schema(id); configured operations via host.data.action(id,params).
Confirm potentially mutating actions explicitly. data.write grants local app writing, not blanket shared database writes. Empty results, missing collection/dataset, revoked grants and schema migration failure are distinct outcomes.
Never claim a DuckDB capability just because the host can use DuckDB internally; CEAPP only consumes its supported Data Bridge surface.

## Clipboard and print

Text: clipboard.writeText. Image Blob: clipboard.writeImage. Small image data URL: copyImageDataURL. Host file copy: copyResult with an authorized result path. The copied object type matters: pixel image, text and file clipboard items are not interchangeable.
Use printHTML for trusted generated markup. User or AI text must be escaped before inserting into printable HTML. This demo uses fixed safe markup. A print dialog is not confirmation that a printer finished.
Use saveImageDataURL for in-memory small image exports. Avoid large data URLs and restore failure/permission state honestly.

## Notifications

The basic profile demonstrates explicit notification.send, getStatus and openSettings with notification.send permission only.
`assets/recipes/advanced-bridges.js` adds opt-in list/register/update/remove examples. Add notification.schedule when incorporating persistent features. The registration snippet matches official demo configuration; it registers feature metadata and does not implement an app's background business producer.
Do not register/re-enable at boot. Respect host tombstones. Re-enable only on an explicit save/re-enable action. Distinguish disabled_by_app, disabled_by_bridge, disabled_globally, permission_revoked, deleted_by_bridge and engine_offline.
Remove test feature registrations after native testing so no lingering schedule is left behind.

## Assets, environment and diagnostics

Use assetURL for package media; smallInline in advanced examples uses assetDataURL for deliberately small content. Prefer a host-injected icon when extending an existing branded app; the Lab has its own demo mark, not a replacement CanEngine logo.
The advanced examples retain current listRuntimes/checkRuntimes/envCheck/envInstall helpers for apps that actually use them. Add dependency declarations based on the current host schema; do not invent dependency IDs.
The visible report redacts secret-like fields, QR/session values and common local paths. Host copyDiagnostics/exportDiagnostics are host-controlled and may include sensitive information; review before sharing. Arbitrary natural-language content can contain secrets beyond heuristic redaction, so never claim comprehensive anonymization.
