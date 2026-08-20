# CEAPP Integration Pitfalls

This document records the most common integration failures when a CEAPP works in a normal browser but fails inside CanEngine. It is intentionally public-safe: it describes the CEAPP-facing contract and troubleshooting logic only, not CanEngine private implementation paths, production endpoints, credentials, session tokens, device identifiers, or internal network details.

## The Most Important Rule

**A capability existing somewhere inside CanEngine does not mean a CEAPP can call it.**

For CEAPP code, the only authoritative native contract is the capability actually exposed through `window.CanEngine` in the running host.

Do not infer APIs from:

- Go or Wails method names
- CanEngine desktop UI behavior
- internal implementation documents
- browser devtools experiments
- another CEAPP that may target a newer host build
- a guessed method name such as `openBrowser()`, `openExternal()` or `phoneBridge.getLatestFile()`

Before using a host feature:

1. Resolve the bridge lazily.
2. Feature-detect the exact method.
3. Check host/capability information when available.
4. Provide a browser or degraded fallback.
5. Do not present the feature as successful until the host call actually succeeds.

Recommended safe resolver:

```js
function getBridge() {
  try {
    if (window.CanEngine) return window.CanEngine
  } catch {}

  try {
    if (window.parent && window.parent !== window && window.parent.CanEngine) {
      return window.parent.CanEngine
    }
  } catch {}

  return null
}
```

Do not cache a missing bridge forever. The safest pattern is to call `getBridge()` when the user triggers an action.

---

## Pitfall 1: Phone Bridge Opens, But The CEAPP Gets No Image

Opening the system Phone Bridge panel and receiving a file inside a specific CEAPP are two different things.

The system panel owns connection and transfer. The CEAPP still needs an explicit application-side intake path.

A reliable design should make these concepts separate:

- **Open system panel**: lets the user connect a phone and manage files.
- **Target current app**: tells the host which CEAPP workflow wants incoming files.
- **Receive event / returned handle**: tells the CEAPP that a file is available.
- **Read/import the file**: converts the host-managed file into the CEAPP's own business state.

### Failure pattern

Bad flow:

```text
Click “Phone Bridge”
→ openPanel()
→ assume the next uploaded image automatically appears in this view
```

This can leave the file in the system Phone Bridge workspace while the CEAPP never imports it.

### Safer flow

```text
User chooses “Import from Phone Bridge”
→ establish the app intake context
→ subscribe to the supported receive callback/event
→ open the Phone Bridge UI or session
→ receive a host-managed file handle
→ pass it into one shared image-import pipeline
→ unsubscribe when the view is destroyed
```

### Important implementation rules

- Subscribe before opening the transfer flow when the public bridge supports events.
- Do not poll an undocumented “latest file” location.
- Do not treat a Phone Bridge file ID as an operating-system path.
- Do not assume files uploaded through the system workspace are automatically attached to the currently visible CEAPP panel.
- If the CEAPP has multiple image targets, such as “pending image” and “cover template”, keep an explicit target state before opening Phone Bridge. Do not infer the target from whichever DOM node happens to be visible later.
- Route desktop picker, drag/drop, paste, and Phone Bridge input into the same normalized `importImage(...)` pipeline.
- Keep a normal file picker as fallback when Phone Bridge is unavailable.

Example architecture:

```js
let pendingImageTarget = null

async function startPhoneImport(target) {
  pendingImageTarget = target
  const bridge = getBridge()
  const phone = bridge?.phoneBridge

  if (!phone) {
    showFallbackFilePicker(target)
    return
  }

  // Only call methods that are actually exposed by the current host.
  // Register the supported receive callback before opening the transfer UI.
}

async function handleReceivedImage(source, target = pendingImageTarget) {
  const normalized = await normalizeImageSource(source)
  applyImageToTarget(target, normalized)
}
```

The exact Phone Bridge method names must come from the current public host contract. Do not invent missing methods from this example.

---

## Pitfall 2: “Open Browser” Works In Chrome But Fails In CanEngine

A CEAPP is not a normal top-level Chrome tab. On different desktop platforms it runs inside the host webview layer, so browser navigation behavior can differ.

Do not call:

- `window.runtime.*`
- Wails runtime methods directly
- guessed `window.CanEngine.openBrowser(...)` or `openExternal(...)` methods
- shell commands such as `open`, `start`, or platform-specific executables from frontend JavaScript

unless the public CEAPP bridge explicitly exposes and authorizes that capability.

### Public-safe fallback

When there is no documented host-native external-browser method:

1. render a normal HTTPS link with clear text;
2. use `target="_blank"` and `rel="noopener noreferrer"` when appropriate;
3. offer “Copy link” as a fallback;
4. do not claim that clicking the action definitely opens the operating-system default browser.

Example:

```html
<a href="https://example.com" target="_blank" rel="noopener noreferrer">
  Open website
</a>
```

If a future CanEngine build exposes an explicit external-navigation bridge, feature-detect it first and keep the link fallback.

---

## Pitfall 3: Importing Images Has Four Different Source Types

Do not use one loading method for every image.

| Image source | Preferred path | Common mistake |
|---|---|---|
| Image bundled inside the CEAPP | `assetURL(appId, path)` | relying only on a relative path inside the host webview |
| Browser-selected `File` / paste | `File` / `Blob` / object URL or stage it | trying to pass a browser File object as a host filesystem path |
| Host-native drag/drop | `onFileDrop` → `stageFile({ sourcePath })` | relying only on iframe DOM `drop` |
| Phone Bridge / host-managed result | supported host handle/read API | assuming the handle is an absolute filesystem path |

### Package assets are not user files

`assetURL()` is for files shipped inside the CEAPP package. It is not a general-purpose file opener.

### Staged files are not package assets

A file selected, dropped, or produced by a job should stay in the host-managed file flow. Use the documented staged/result helpers to preview, process, export, open, or reveal it.

### Never persist absolute paths into app state when a stable host handle is available

Absolute paths are machine-specific, privacy-sensitive, and easy to break after moving files or switching platforms.

---

## Pitfall 4: Desktop Drag/Drop Is Not The Same As Browser Drag/Drop

Inside an embedded CEAPP, Finder / Explorer file drops may not reach the inner iframe exactly like they reach a normal browser tab.

For important desktop file intake:

- Keep HTML5 `dragover` / `drop` for standalone browser debugging.
- Use `window.CanEngine.onFileDrop(...)` as the host-safe path when exposed.
- Stage host-native paths before reading them.
- Normalize both paths into one application import function.

Do not duplicate business logic between picker, drop, paste, and Phone Bridge flows.

---

## Pitfall 5: A Bridge Method Can Exist But Still Be Unusable

There are at least four separate checks:

1. The host version contains the feature.
2. The CEAPP bridge exposes the method.
3. The manifest declares the needed permission/capability.
4. The user/environment currently allows the action.

So this is unsafe:

```js
await window.CanEngine.someCapability.doThing()
showSuccess()
```

Prefer:

```js
const bridge = getBridge()
const method = bridge?.someCapability?.doThing

if (typeof method !== 'function') {
  showUnsupportedState()
  return
}

try {
  const result = await method.call(bridge.someCapability, request)
  showSuccess(result)
} catch (error) {
  showActionableError(error)
}
```

Do not hide permission, runtime, network, or host-version failures behind a generic “Unknown error”.

---

## Pitfall 6: Browser Success Is Not Host Success

Always test both paths when the app is intended for CanEngine:

### Standalone browser

Useful for:

- layout
- pure JavaScript logic
- browser file picker
- browser paste
- fallback links

### CanEngine host

Required for validating:

- package asset loading
- host-native file drop
- staged files
- jobs and runtimes
- AI Bridge
- Notification Bridge
- Phone Bridge
- save/open/reveal actions
- permission behavior

A feature that only works in Chrome is not finished if its primary production environment is CanEngine.

---

## Pitfall 7: Do Not Cache UI Context Through A Transfer Flow

Phone uploads, native dialogs, AI jobs, and runtime jobs are asynchronous. During the wait, the user may switch tabs, close a modal, or create another item.

Bad pattern:

```js
openPhoneBridge()
// later: querySelector('.selected-card') and hope it is still the same target
```

Better pattern:

```js
const requestContext = {
  targetId: currentTargetId,
  purpose: 'cover-template'
}

await beginImport(requestContext)
```

Persist stable application IDs, not fragile DOM references.

---

## Pitfall 8: Event Listeners Need Lifecycle Cleanup

Repeatedly opening a page or modal can accidentally register duplicate bridge listeners. The same uploaded file may then be processed two or more times.

Rules:

- store every unsubscribe function returned by bridge event APIs;
- unsubscribe when the view/modal is destroyed;
- avoid registering the same global listener on every button click;
- make file-import handlers idempotent where practical.

---

## Pitfall 9: Manifest Declarations Do Not Create Native Features

Adding a permission string to `app.json` does not magically add a host API.

Permissions should only describe capabilities the host already understands and enforces. Never invent permissions as a substitute for implementing/exposing the actual bridge feature.

Also keep `appId` consistent between:

- `app.json`
- bridge calls
- staged files
- job requests
- app-owned notification features
- Phone Bridge targeting, when supported

A mismatched `appId` can look like a bridge bug while actually being an application identity bug.

---

## Pitfall 10: Public Repository Hygiene

Before publishing a CEAPP or Skill repository, search the entire tree for information that should stay private.

Do not commit:

- access tokens, API keys, cookies, passwords, private keys, signing keys
- real session IDs, pairing codes, QR payloads, license values, device identifiers
- production-only internal endpoints or debug endpoints
- private LAN addresses or machine-specific absolute paths
- home-directory usernames
- raw diagnostics containing local paths or account/device metadata
- internal architecture handoff documents that reveal implementation details unrelated to the public CEAPP contract
- `.DS_Store`, IDE state, logs, temporary exports, generated archives, or test credentials

Public product/download URLs are fine when they are intentionally public. Private operational endpoints are not.

Recommended pre-publish checks:

```bash
git status --short
git ls-files
grep -RniE '(token|secret|password|private.?key|api.?key|session|license)' . --exclude-dir=.git
```

Review matches manually. A keyword match is not automatically a secret, and a secret may use an unexpected name.

---

## Pre-Release Integration Checklist

- [ ] The app resolves `window.CanEngine` safely and lazily.
- [ ] Every critical bridge method is feature-detected.
- [ ] No CEAPP code calls `window.runtime.*` directly.
- [ ] External-link behavior has a non-native fallback.
- [ ] Package images use host-safe asset loading.
- [ ] Browser picker, native drop, paste, and Phone Bridge converge on one import pipeline where applicable.
- [ ] Phone Bridge opening and app-specific file intake are treated as separate steps.
- [ ] Multiple image targets carry an explicit target ID through async flows.
- [ ] Bridge event listeners are unsubscribed correctly.
- [ ] Manifest permissions are minimal and correspond to real host capabilities.
- [ ] The app has been tested inside CanEngine, not only in Chrome.
- [ ] No secrets, private endpoints, machine paths, pairing data, or raw diagnostics are committed.
