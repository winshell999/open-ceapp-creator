# Manifest And Host Bridge

## Preferred App Layout (Current CanEngine)

For new nontrivial apps, prefer:

```text
Apps/MyApp/
├── ceapp/
│   ├── app.json
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   ├── assets/
│   │   ├── ceapp-i18n.js
│   │   └── logo.png
│   └── scripts/
│       └── backend_or_cli_if_needed
└── README.md
```

Legacy apps may keep a flatter layout:

```text
Apps/MyLegacyApp/
├── app.json
├── index.html
├── ...
```

When updating an existing app, prefer staying consistent with the local pattern unless the task is explicitly about restructuring it.

## Manifest Baseline

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
  "description": "Short app description.",
  "descriptionI18n": {
    "zh-CN": "简短应用说明。",
    "en-US": "Short app description."
  },
  "entry": "index.html",
  "icon": "assets/logo.png",
  "minCanEngineVersion": "1.4.1",
  "platforms": [{ "os": "*", "arch": "*" }],
  "runtime": {
    "requirements": [
      { "id": "base-runtime" }
    ]
  },
  "commands": {
    "noop": {
      "executable": "echo",
      "baseArgs": ["my-app"]
    }
  },
  "capabilities": {
    "ai": {
      "required": false,
      "features": []
    }
  },
  "permissions": []
}
```

## Command Requirement (Current Packer)

The current CanEngine packer rejects an `app.json` with an empty `commands` object.

For a pure UI app that does not truly run a backend task, declare a minimal inert command:

```json
"commands": {
  "noop": {
    "executable": "echo",
    "baseArgs": ["my-app"]
  }
}
```

Rules:

- Use a stable app-specific token in `baseArgs`.
- Do not wire the UI to the dummy command.
- Replace the dummy command with a real one as soon as the app genuinely needs host-run execution.

## Icon Notes

- `icon` should be a package-relative path.
- Prefer `assets/logo.png` as the default convention.
- Prefer PNG with square dimensions and clean small-size readability.
- Do not use remote URLs, absolute paths, or machine-specific paths.
- Even if the current host falls back to a default icon in some surfaces, ship a real app logo in the package.

If the app has an internal page header that should visually match the icon shown in the CanEngine app list, prefer the host-injected icon first:

```js
const APP_ICON_SRC = window.__CANENGINE_APP_ICON__ || 'assets/logo.png'
```

This avoids image-path surprises inside the injected launch surface while keeping a local package fallback.

## Local Asset Loading Strategy

Hosted ceapps do not behave exactly like a plain `file://` browser page.

Current launch model:

- the host reads and prepares the app HTML
- scripts and styles may be inlined or rewritten before launch
- images referenced later by HTML or CSS still depend on webview file-loading behavior

That means:

- `img src="assets/logo.png"` may look fine in Chrome
- the same path may fail, appear inconsistently, or be blocked inside the hosted CanEngine webview

Treat local assets in four buckets:

### 1. Plain relative assets

Use for:

- noncritical decorative images
- assets whose failure does not break the user’s understanding

Examples:

- secondary illustrations
- optional decorative textures
- nonessential empty-state decoration

### 2. Host-served package assets

Use for:

- package-local images, audio, and video rendered inside CanEngine
- large media files that should not be converted to base64 strings
- critical UI images whose failure would make the app look broken

Recommended form:

```js
const bridge = window.CanEngine || (window.parent && window.parent.CanEngine)

const imageURL = await bridge.assetURL('my-app', 'assets/demo.png')
document.querySelector('img').src = imageURL

audio.src = await bridge.assetURL('my-app', 'assets/demo.mp3')
audio.load()

video.src = await bridge.assetURL('my-app', 'assets/demo.mp4')
video.poster = await bridge.assetURL('my-app', 'assets/poster.png')
video.load()
```

Fallback for direct browser debugging:

```js
async function packagedAsset(appId, assetPath) {
  const bridge = window.CanEngine || (window.parent && window.parent.CanEngine)
  if (bridge?.assetURL) return bridge.assetURL(appId, assetPath)
  return new URL(assetPath, document.baseURI).toString()
}
```

### 3. Inline critical assets

Use for:

- small images that must always appear
- first-screen branding
- critical status art

Recommended forms:

- data URL
- build-time inlined asset string
- `assetDataURL(appId, assetPath)` for small inline/copy-only cases

Do not use `assetDataURL` for large images, audio, or video by default. It duplicates the whole file into JS memory as a base64 string.

### 4. Host-injected assets

Use for:

- app header logos that should match the CanEngine app list
- any image the host already knows how to provide safely

Current built-in example:

```js
const APP_ICON_SRC = window.__CANENGINE_APP_ICON__ || 'assets/logo.png'
```

## Critical Image Rule

If an image failing to load would make the app look broken, confusing, or untrustworthy, do **not** rely only on:

- `img src="assets/..."`
- `background-image: url('assets/...')`

Prefer, in order:

1. host-injected source
2. `assetURL(appId, assetPath)`
3. `assetDataURL(appId, assetPath)` only for small inline/copy cases
4. plain relative path only for noncritical assets

Good examples of critical images:

- header logos
- loading / status illustrations
- must-show action icons
- first-view hero or brand image
- any image used to communicate completion, failure, or identity

## Host Bridge Usage

The app may access the host bridge from:

```js
window.CanEngine || (window.parent && window.parent.CanEngine)
```

The bridge is the authoritative ceapp-to-host contract. If a capability is not available on `window.CanEngine`, do not assume the app can reach it just because it exists somewhere in Wails or Go.

### Browser-First Development Contract

Most ceapps are first debugged in a normal browser and only later loaded into CanEngine. Design for that from day one:

- Always resolve the bridge lazily:

```js
function getBridge() {
  return window.CanEngine || (window.parent && window.parent.CanEngine) || null
}
```

- Every bridge use must be optional:
  - if bridge exists, use host capability
  - if bridge is missing, use a browser fallback or a degraded but nonbroken local path
- Do not call `window.runtime.*` directly from ceapp code.
  - `window.runtime.*` belongs to the outer Wails host shell, not to the ceapp contract.
  - If the app needs a new host feature, add it to `window.CanEngine` in the host and document it here.

### Current Bridge Surface (Exhaustive)

These are the methods currently exposed to ceapps on `window.CanEngine`.

#### File input and drag/drop

- `stageFile(request: { appId: string, name?: string, dataBase64?: string, sourcePath?: string }) => Promise<StagedFile>`
  - Use `dataBase64` when staging a file already held in browser memory.
  - Use `sourcePath` when the host gives you a real OS file path, such as native file drop.
  - When `sourcePath` is provided, the host can derive `name` automatically from the filename.
- `stageFileDialog(appId: string) => Promise<StagedFile>`
- `stageFilesDialog(appId: string) => Promise<StagedFile[]>`
- `onFileDrop(handler: ({ x: number, y: number, paths: string[] }) => void) => unsubscribe`
  - This is the host-native file-drop bridge for dragging files from Finder / Explorer into CanEngine.
  - In hosted ceapps, OS file drag into the inner iframe may not reliably reach inner DOM `drop` listeners.
  - Prefer `onFileDrop(...)` for desktop file-drop workflows, then stage each `sourcePath` with `stageFile({ appId, sourcePath })`.

#### Packaged assets

- `assetURL(appId: string, assetPath: string) => Promise<string>`
  - Preferred for assigning package-local image/audio/video URLs to `src` or `poster`.
  - Does not base64-copy the whole media file into JS memory.
- `assetDataURL(appId: string, assetPath: string) => Promise<string>`
  - Use only for small inline assets, clipboard/copy flows, or cases that require a `data:` URL.

#### Jobs and long-running work

- `runJob(request: { appId: string, commandId: string, args?: string[], inputFileIds?: string[], mode?: string }) => Promise<JobInfo>`
- `cancelJob(jobId: string) => Promise<void>`
- `onEvent(name: string, handler: (payload: any) => void) => unsubscribe`
  - Use this for host event streams such as job updates.

#### Results and output handling

- `resultDataURL(path: string) => Promise<string>`
  - Reads a staged or result file and returns a `data:` URL.
- `saveAs(path: string) => Promise<string>`
  - Opens the host save dialog for an existing staged/result path and returns the saved target path.
- `saveImageDataURL(defaultFilename: string, dataURL: string) => Promise<string>`
  - Host-native “save generated image bytes” helper for in-memory image output.
- `copyResult(path: string) => Promise<void>`
- `copyImageDataURL(dataURL: string) => Promise<void>`
- `openResult(path: string) => Promise<void>`
- `revealResult(path: string) => Promise<void>`

#### Runtime and environment management

- `listRuntimes() => Promise<PlatformRuntime[]>`
- `checkRuntimes(runtimeIds: string[]) => Promise<PlatformRuntime[]>`
- `installRuntime(runtimeId: string) => Promise<RuntimeInstallResult>`
- `getAppRuntimeStatus(appId: string) => Promise<AppRuntimeStatusResult>`
- `envCheck(appId: string) => Promise<EnvCheckResult>`
- `envInstall(appId: string, dependencyId: string) => Promise<EnvInstallResult>`

#### Host-injected globals

- `window.__CANENGINE_APP_ICON__`
  - The host-injected app-list icon as a data URL or host-safe image source.
  - Prefer this value for in-app header logos when you want exact visual alignment with the CanEngine app list.

#### Locale sync

- `getLocale() => string | Promise<string>`
- `setLocale(locale: string) => string | Promise<string>`
- `onLocaleChange(handler: (locale: string) => void) => unsubscribe`

#### AI Bridge (CanEngine 1.4.1+)

AI Bridge is exposed under `window.CanEngine.ai`. API Keys, provider routes, Base URLs, user authorization, limits, and usage logs stay in the host. A ceapp only declares capabilities and sends task input.

- `ai.getStatus() => Promise<AIBridgeStatus>`
- `ai.text.generate(request: TextGenerateRequest) => Promise<TextGenerateResponse>`
- `ai.vision.analyze(request: VisionAnalyzeRequest) => Promise<VisionAnalyzeResponse>`
- `ai.image.generate(request: ImageGenerateRequest) => Promise<ImageGenerateResponse>`
- `ai.model3d.generate(request: Model3DGenerateRequest) => Promise<Model3DTask>`
- `ai.model3d.getTask(taskId: string) => Promise<Model3DTaskStatus>`
- `ai.model3d.cancelTask(taskId: string) => Promise<void>`
- `ai.video.create(request: VideoCreateRequest) => Promise<VideoTask>`
- `ai.video.getTask(taskId: string) => Promise<VideoTaskStatus>`
- `ai.video.cancelTask(taskId: string) => Promise<void>`

Manifest requirements:

```json
"minCanEngineVersion": "1.4.1",
"capabilities": {
  "ai": {
    "required": false,
    "features": [
      "ai.text.generate",
      "ai.vision.analyze",
      "ai.image.generate",
      "ai.model3d.generate",
      "ai.video.generate"
    ]
  }
},
"permissions": [
  "ai.text.generate",
  "ai.vision.analyze",
  "ai.image.generate",
  "ai.model3d.generate",
  "ai.video.generate"
]
```

Use `required: false` unless the app cannot provide any useful experience without AI.

Do not ask for API Keys inside a ceapp. If a call fails with `AI_BRIDGE_NOT_CONFIGURED`, `AI_FEATURE_DISABLED`, or `AI_PERMISSION_DENIED`, show a friendly degraded state and tell the user to configure or authorize AI Bridge in CanEngine “我的”.

Example text call:

```js
const bridge = window.CanEngine || (window.parent && window.parent.CanEngine)
const response = await bridge.ai.text.generate({
  messages: [{ role: 'user', content: 'Summarize this note.' }],
  maxTokens: 300
})
console.log(response.text)
```

Example image input for vision:

```js
const staged = await bridge.stageFile({
  appId: 'my-app',
  name: file.name,
  dataBase64: await readFileAsDataURL(file)
})

const response = await bridge.ai.vision.analyze({
  prompt: 'Describe this image.',
  images: [{ type: 'temp-file', path: staged.path }],
  maxTokens: 500
})
```

### Current Data Shapes

Important return/request shapes currently used by the bridge:

```ts
type StageFileRequest = {
  appId: string
  name?: string
  dataBase64?: string
  sourcePath?: string
}

type StagedFile = {
  id: string
  appId: string
  name: string
  path: string
  size: number
  createdAt: string
}

type JobRequest = {
  appId: string
  commandId: string
  args?: string[]
  inputFileIds?: string[]
  mode?: string
}

type ResultFile = {
  name: string
  path: string
  type: string
  mime: string
  size: number
}

type TextGenerateRequest = {
  messages: Array<{ role: 'system' | 'user' | 'assistant', content: string }>
  temperature?: number
  maxTokens?: number
  model?: string
}

type TextGenerateResponse = {
  text: string
  usage?: { inputTokens?: number, outputTokens?: number, totalTokens?: number }
}

type AIMediaInput = {
  type?: 'temp-file' | 'ceapp-asset' | 'data-url'
  path: string
}

type VisionAnalyzeRequest = {
  prompt: string
  images?: AIMediaInput[]
  maxTokens?: number
  model?: string
}

type ImageGenerateRequest = {
  prompt: string
  size?: string
  count?: number
  model?: string
}
```

For runtime/environment responses, the important rule is:

- do not invent fields
- inspect the current local Go types if you need exact shape
- when documenting app behavior, describe the fields you actually consume

### Desktop Dragging Rule

Treat browser DOM drag/drop and host-native file drop as two different paths:

- Standalone browser path:
  - HTML5 `dragover` / `drop`
  - `event.dataTransfer.files`
- Hosted CanEngine path:
  - `bridge.onFileDrop(...)`
  - `bridge.stageFile({ appId, sourcePath })`
  - `bridge.resultDataURL(path)` when preview bytes are needed

The safest pattern for file-drop tools is:

1. keep DOM `drop` for standalone browser use
2. add `bridge.onFileDrop(...)` for hosted desktop use
3. normalize both paths into one shared `loadFile(...)` or `loadStagedFile(...)` flow

For image inputs, also support paste when feasible:

```js
document.addEventListener('paste', async (event) => {
  if (['INPUT', 'TEXTAREA'].includes(event.target?.tagName)) return
  const files = Array.from(event.clipboardData?.items || [])
    .filter((item) => item.kind === 'file' && item.type.startsWith('image/'))
    .map((item) => item.getAsFile())
    .filter(Boolean)
  for (const file of files) {
    event.preventDefault()
    await handleImageFile(file)
  }
})
```

Do not assume the host currently provides:

- bluetooth
- wifi
- geolocation
- arbitrary sensor access
- unrestricted shell execution

## Platform Runtime Preference

Prefer shared CanEngine runtimes for first-party apps instead of making each app manage its own installer UX.

Current runtime ids:

- `base-runtime`
- `ai-image-runtime`
- `video-runtime`
- `advanced-analysis-runtime`

Recommended pattern:

1. declare `runtime.requirements` in `app.json`
2. detect readiness with `getAppRuntimeStatus(appId)`
3. request installs with `installRuntime(runtimeId)`
4. keep `environment.dependencies` only when you still need legacy `envCheck` / `envInstall` fallback support

## Critical Interaction Guidance

When writing a demo or app spec, explicitly document the path for:

- dragging
- copying text
- copying images
- copying GIFs or files
- file input
- file output

For each interaction, say whether it is:

- browser-only
- host bridge
- browser first with host fallback
- host first with browser fallback

If the app is expected to run inside CanEngine, prefer the path that survives embedded webview behavior instead of the path that merely works in a standalone Chrome tab.

### Dragging

- Do not assume HTML5 `dragstart` / `dataTransfer` is sufficient for key workflows.
- Do not assume OS file drag from Finder / Explorer into a hosted iframe will behave like a normal browser tab.
- For file-drop tools inside ceapps, treat `bridge.onFileDrop(...)` as the host-safe path and DOM `drop` as the standalone-browser fallback.
- For toolbox-to-canvas or similar desktop-tool interactions, prefer self-managed pointer/mouse dragging when webview stability matters.

### Copy Actions

- Do not assume `navigator.clipboard.write()` is sufficient for image copy in the host.
- Prefer the CanEngine host bridge for image, GIF, or file clipboard behavior when available.
- Define exactly what each “Copy” action means:
  - text
  - command
  - image pixels
  - GIF as file clipboard item
  - file path
  - download link

## Demo-To-ceapp Checklist

Before turning a demo into a packaged ceapp, check:

1. Are there any CDN or remote startup dependencies?
2. Are there remote images in the critical workflow?
3. Does drag/drop rely only on `dragstart` / `dataTransfer`?
4. Does image copy rely only on browser clipboard APIs?
5. Is there a host-bridge alternative for key desktop actions?
6. Has the runtime strategy been chosen and documented?
7. Is `commands` non-empty in `app.json`?
8. Is the package source isolated from `demo/`, `OLD/`, archives, and design source?
9. Do package-local media assets use `assetURL` rather than large `data:` URLs?
10. Do image-upload surfaces support picker, native drop, browser drop, and paste where applicable?

## Runtime Reality

The app is not hosted inside a uniform bundled Chrome runtime today. It is hosted inside the CanEngine webview layer:

- macOS: WKWebView / WebKit-family behavior
- Windows: WebView2 / Chromium-family behavior

So compatibility must be validated against the host path, not only a local browser tab.

Locale bridge APIs commonly include:

- `getLocale()`
- `setLocale(locale)`
- `onLocaleChange(handler)`

## Locale Notes

- Use the shared `ceapp-i18n.js` helper whenever possible.
- The helper should survive standalone browser use and embedded CanEngine use.
- Keep the helper local inside the app package.
- If the app should follow the CanEngine platform locale, do not add a duplicate in-app locale toggle unless the user explicitly asks for one.

## Permissions Notes

`permissions` should be treated as a conservative declaration layer.

- Declare only real needs.
- Do not invent a permission unless the host is also updated to interpret and enforce it.
- Do not assume a manifest permission gives access to native OS capabilities by itself.

## Packaging Handoff Notes

This open skill should produce a clean CEAPP source project directory. The final `.ceapp` container should be created by CanEngine, not by the skill.

Recommended flow:

1. Generate or update the CEAPP source project.
2. Ensure the project root contains `app.json`, `index.html`, local CSS / JS, and needed `assets/`.
3. Open CanEngine.
4. Go to `我的 → 开发者身份 / CEAPP打包与签名`.
5. Drag the CEAPP project root folder into the packaging area.
6. CanEngine validates, packages, signs, and exports the final `.ceapp`.

Packaging rules:

- Read the CEAPP app version from the app's own `app.json`.
- Do not use the CanEngine host version as the CEAPP app version.
- The skill must not embed official signing credentials, KOL signing credentials, private-key paths, or default trusted key IDs.
- Official and KOL signing must be performed by CanEngine client/backend flows, not by public skill scripts.
- Self-signed output is only a source/risk label; it is not official certification or security review.
