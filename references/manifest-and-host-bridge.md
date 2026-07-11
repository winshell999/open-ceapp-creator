# Manifest and Host Bridge

Use this reference when editing `app.json` or calling `window.CanEngine`. It reflects the CanEngine 1.5.9 host contract while keeping the CEAPP's own version lifecycle independent.

## Contents

1. Project layout
2. Manifest baseline
3. Capability and permission recipes
4. Bridge access and browser fallback
5. Package assets
6. File input and staging
7. App-private data
8. Jobs, results, and runtime
9. Diagnostics, locale, print, and clipboard
10. Optional bridge surfaces
11. Final consistency checklist

## 1. Project layout

Use a self-contained project root:

```text
my-app/
├── app.json
├── index.html
├── app.js
├── styles.css
├── assets/
│   ├── ceapp-i18n.js
│   └── logo.png
├── data/
│   └── localdb.schema.json   # only for declared local Data Bridge
└── scripts/
    └── worker.py             # only for declared commands
```

Keep source-only docs, design files, archives, old builds, secrets, and caches outside the package root.

## 2. Manifest baseline

```json
{
  "schemaVersion": 1,
  "appId": "my-app",
  "name": "My App",
  "nameI18n": {
    "zh-CN": "我的应用",
    "en-US": "My App"
  },
  "version": "1.0.0",
  "description": "A short product description.",
  "descriptionI18n": {
    "zh-CN": "简短的产品说明。",
    "en-US": "A short product description."
  },
  "entry": "index.html",
  "icon": "assets/logo.png",
  "minCanEngineVersion": "1.5.8",
  "platforms": [{ "os": "*", "arch": "*" }],
  "commands": {
    "noop": {
      "executable": "echo",
      "baseArgs": ["my-app"],
      "allowedFlags": []
    }
  },
  "permissions": []
}
```

Current validation rules that commonly fail:

- `schemaVersion` must be `1`.
- `appId` must be 2-64 lowercase letters, digits, hyphens, underscores, or dots.
- `entry`, icon, schema, scripts, and database filenames must be package-relative.
- `commands` must contain at least one command. Keep an inert `noop` only for pure UI apps and never wire it to the UI.
- Every command needs an executable. Treat `allowedFlags` as a strict allowlist.
- AI, Data Bridge, and Notification Bridge capability metadata must have matching flat permissions.
- A CEAPP's `version` is not the CanEngine host version. Increment it when distributing an update.
- Changing `appId` changes app identity and app-private data identity.

## 3. Capability and permission recipes

Start with no optional capability. Add one recipe only when the app has a user-visible feature that calls it.

### App-private local data

```json
{
  "capabilities": {
    "dataBridge": {
      "required": false,
      "local": {
        "enabled": true,
        "dbFile": "my-app.sqlite",
        "schemaEntry": "data/localdb.schema.json",
        "schemaVersion": 1
      }
    }
  },
  "permissions": ["data.read", "data.write"]
}
```

Minimal schema:

```json
{
  "collections": ["notes"]
}
```

Remove `data.write` for a genuinely read-only local feature. Do not put `data.local` in permissions; it is an API name, not a permission.

### Shared dataset or action

```json
{
  "capabilities": {
    "dataBridge": {
      "required": false,
      "datasets": ["declared_dataset_id"],
      "actions": ["declared_action_id"],
      "mode": "read"
    }
  },
  "permissions": ["data.read", "data.action"]
}
```

Declare exact resource IDs supplied for the product. Do not invent wildcard datasets/actions or expose direct SQL and database credentials.

### AI text generation

```json
{
  "capabilities": {
    "ai": {
      "required": false,
      "features": ["ai.text.generate"]
    }
  },
  "permissions": ["ai.text.generate"]
}
```

Supported feature permissions include:

- `ai.text.generate`
- `ai.vision.analyze`
- `ai.image.generate`
- `ai.model3d.generate`
- `ai.video.generate`

Declare only features the UI calls. Keep `required: false` when the useful core can work without AI.

### Immediate notification

```json
{
  "capabilities": {
    "notification": {
      "required": false,
      "reason": "Notify the user after an explicit long-running export.",
      "capabilities": ["send"]
    }
  },
  "permissions": ["notification.send"]
}
```

Add `schedule` and `notification.schedule` only when the app registers a persistent schedule/event feature.

### Phone Bridge

Phone Bridge uses flat permissions without a `capabilities.phoneBridge` block. Read `phone-bridge.md` and declare only called methods.

## 4. Bridge access and browser fallback

Resolve the bridge lazily:

```js
function getBridge() {
  return window.CanEngine || (window.parent && window.parent.CanEngine) || null
}
```

Rules:

- Use only methods exposed on `window.CanEngine`; never call outer Wails internals such as `window.runtime`.
- Detect an optional method immediately before use.
- Keep the local shell functional when the bridge is absent.
- Use a browser fallback only when it preserves the same product meaning.
- Show unavailable, denied, loading, success, and error states instead of hiding failures.
- Do not expose raw response objects when they contain paths, tokens, URLs, file content, or credentials.

Host discovery:

```js
const bridge = getBridge()
const version = await bridge?.getHostVersion?.()
const capabilities = await bridge?.getCapabilities?.()
const hasPhoneBridge = await bridge?.hasCapability?.('phone.bridge')
```

`getHostVersion()` returns an object with `hostVersion`, `apiVersion`, and `platform`.

## 5. Package assets

Use `assetURL` for normal package image/audio/video rendering:

```js
async function packageAsset(path) {
  const bridge = getBridge()
  if (bridge?.assetURL) {
    try {
      return await bridge.assetURL(APP_ID, path)
    } catch {
      // Fall through to standalone-browser debugging.
    }
  }
  return new URL(path, document.baseURI).toString()
}

image.src = await packageAsset('assets/example.png')
audio.src = await packageAsset('assets/example.mp3')
video.src = await packageAsset('assets/example.mp4')
video.poster = await packageAsset('assets/poster.png')
```

Use `assetDataURL(appId, path)` only when a small inline/copy workflow specifically requires a data URL. Large media in a data URL duplicates bytes in memory.

Package-relative paths remain useful as the standalone-browser fallback, but a critical hosted image should not rely on a plain relative URL alone.

## 6. File input and staging

Treat these as separate inputs that converge on shared business logic:

- browser picker: `input.files`
- browser drop: `event.dataTransfer.files`
- clipboard paste: `ClipboardEvent.clipboardData.items`
- native desktop drop: `onFileDrop`
- host dialog: `stageFileDialog` or `chooseFile`
- Phone Bridge: descriptor followed by `readFile(fileId)`

### Browser File

Preview with an object URL and revoke it when replaced:

```js
let previewURL = ''

function previewFile(file) {
  if (previewURL) URL.revokeObjectURL(previewURL)
  previewURL = URL.createObjectURL(file)
  image.src = previewURL
}
```

### Stage in-memory bytes

`stageFile` accepts `dataBase64`, not a raw `File` field. Use a data URL only for the staging request; keep object URLs for normal preview.

```js
function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(reader.error)
    reader.onload = () => resolve(String(reader.result || ''))
    reader.readAsDataURL(file)
  })
}

const staged = await bridge.stageFile({
  appId: APP_ID,
  name: file.name,
  dataBase64: await readAsDataURL(file),
  mime: file.type
})
```

### Native desktop drop

```js
const unsubscribe = bridge.onFileDrop(async ({ paths = [] }) => {
  for (const sourcePath of paths) {
    const staged = await bridge.stageFile({ appId: APP_ID, sourcePath })
    await handleStagedFile(staged, 'host-native-drop')
  }
})
```

Never show `sourcePath` in normal UI or copied diagnostics. Browser DOM drop remains the standalone fallback because native drag into an embedded view may not reach the inner DOM reliably.

Useful file methods:

- `stageFile(request)`
- `getStagedFile(fileId)`
- `removeStagedFile(fileId)`
- `stageFileDialog(appId)` / `stageFilesDialog(appId)`
- `chooseFile(options)` / `chooseFiles(options)`
- `chooseDirectory(options)`
- `onFileDrop(handler)`

## 7. App-private data

The current local collection surface is exactly:

```js
const notes = bridge.data.local('notes')

await notes.put({ id: 'note-1', title: 'Hello', createdAt: new Date().toISOString() })
const one = await notes.get('note-1')
const result = await notes.find({ limit: 50 })
await notes.delete('note-1')
```

`find` returns `{ ok, rows, count }`. Persist app records without absolute paths or credentials. If migrating older `localStorage` data, delete the old value only after every Data Bridge write succeeds.

Shared data uses:

```js
const result = await bridge.data.dataset('declared_dataset_id').find({
  where: { status: 'active' },
  sort: [{ field: 'updated_at', direction: 'desc' }],
  limit: 20
})

const schema = await bridge.data.schema('declared_dataset_id')
const actionResult = await bridge.data.action('declared_action_id', { status: 'active' })
```

Use a declared action for complex shared queries. Do not connect a CEAPP directly to a shared database.

## 8. Jobs, results, and runtime

Declare a real command and its runtime only when the product needs host-run work:

```json
{
  "runtime": {
    "requirements": [{ "id": "python-runtime", "optional": true }]
  },
  "commands": {
    "process": {
      "executable": "python3",
      "baseArgs": ["scripts/process.py"],
      "allowedFlags": ["--mode"]
    }
  }
}
```

Prefer current runtime discovery:

```js
const runtime = await bridge.requireRuntime('python-runtime')
if (!runtime.ok) showRuntimeUnavailable(runtime.message)
```

Run a job with staged file IDs:

```js
const job = await bridge.runJob({
  appId: APP_ID,
  commandId: 'process',
  inputFileIds: [staged.id],
  args: ['--mode', 'fast']
})
```

Job methods:

- `runJob(request)`
- `getJob(jobId)`
- `listJobs(filter)`
- `getJobLogs(jobId)`
- `cancelJob(jobId)`
- `onEvent(name, handler)`

Prefer managed result references:

- `exportFile({ jobId, fileRef, suggestedName })`
- `openFile({ jobId, fileRef })`
- `revealFile({ jobId, fileRef })`

Path-based result helpers exist for compatibility, but paths should not become the public app contract or appear in shareable logs.

## 9. Diagnostics, locale, print, and clipboard

Diagnostics:

- `getDiagnostics(appId)`
- `copyDiagnostics(appId)`
- `exportDiagnostics(appId)`

Prefer a small app-owned diagnostic summary containing app version, host version, capability booleans, locale, and permission names. Remove path-, token-, URL-, content-, and byte-like fields before copying.

Locale:

- `getLocale()`
- `onLocaleChange(handler)`
- `setLocale(locale)` only for a demo/settings feature intended to change the platform language

Use the bundled `ceapp-i18n.js` and keep both `zh-CN` and `en-US` message tables local.

Print:

```js
await bridge.printHTML(completeHTMLDocument, { title: 'Report' })
```

Clipboard:

```js
await bridge.clipboard.writeText(text)
await bridge.clipboard.writeImage(dataURL)
```

Use browser clipboard only as a fallback. Define whether a copy action copies text, image pixels, a file, or a result reference.

## 10. Optional bridge surfaces

AI Bridge:

```js
const response = await bridge.ai.text.generate({
  messages: [{ role: 'user', content: prompt }],
  maxTokens: 300
})
```

Provider keys, base URLs, limits, and authorization stay in CanEngine. Handle disabled, not configured, feature disabled, permission denied, timeout, and provider errors.

Vision uses a staged temporary file rather than large base64 in the AI request:

```js
const response = await bridge.ai.vision.analyze({
  prompt: 'Describe this image.',
  images: [{ type: 'temp-file', path: staged.path }],
  maxTokens: 500
})
```

Notification Bridge:

```js
await bridge.notification.send({
  title: 'Export complete',
  content: 'Your result is ready.',
  level: 'info',
  category: 'export'
})
```

Persistent notification features additionally use `registerFeature`, `updateFeature`, `removeFeature`, `listOwnFeatures`, `getStatus`, and `openSettings`. The app owns feature creation and its source-side switch; the bridge governs permission and delivery.

Phone Bridge is covered in `phone-bridge.md` because receive/send flows and privacy rules need focused handling.

## 11. Final consistency checklist

1. `app.json` and JavaScript use the same `appId`.
2. The app-owned version changed only when the app changed; it does not mirror the host release.
3. `nameI18n` and `descriptionI18n` contain `zh-CN` and `en-US`.
4. Every capability metadata item has its required permission.
5. Every permission maps to called code and a user-visible feature.
6. `commands` is non-empty; every real command has a narrow flag allowlist.
7. First-screen CSS/JS/fonts/icons are local.
8. Package media uses `assetURL` and large media avoids data URLs.
9. File sources normalize before business logic; object URLs are revoked.
10. Optional bridges have disabled/denied/error states.
11. Shareable UI and diagnostics omit paths, session URLs, tokens, credentials, and file bodies.
12. Browser fallback and installed CanEngine behavior have both been tested.
