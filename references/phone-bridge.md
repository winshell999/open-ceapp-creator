# Phone Bridge for Public CEAPP Source

Use Phone Bridge when users need to move files from a phone into a desktop CEAPP or explicitly send CEAPP output back to a phone. Keep a normal file picker fallback whenever possible.

As of the current CanEngine public contract sync, Phone Bridge remains a **host-level system capability**. CEAPPs use the Host API; they do not own the LAN transfer server, discovery protocol, connection code, or temporary workspace. The Host API compatibility line remains `2026-07`.

## Public-safe boundary

- Phone Bridge is a CanEngine system capability, not a CEAPP-owned server.
- Call only methods actually exposed through `window.CanEngine.phoneBridge`; do not infer APIs from CanEngine desktop UI or private implementation details.
- Do not create a custom LAN listener for normal phone intake.
- Never log or publish QR payloads, session URLs, tokens, pairing codes, private IP addresses, device identifiers, or desktop paths.
- Do not persist a session descriptor. Create a new short-lived session when the user asks.
- Degrade to a picker or clear unavailable state outside CanEngine.

## The key integration rule

**Opening Phone Bridge and importing a file into the current CEAPP target are separate operations.**

A system Phone Bridge panel may successfully receive a file while the CEAPP still receives nothing. The application must maintain its own intake context and explicitly route the host-managed file into the intended business target.

Bad assumption:

```text
open Phone Bridge
→ upload succeeds
→ assume the currently visible image slot now owns that file
```

Recommended flow:

```text
user chooses “Import from phone”
→ capture stable targetId/purpose
→ establish the supported receive callback/session
→ open Phone Bridge
→ receive host-managed file descriptor
→ read/normalize the file
→ import into that targetId
→ clean up the listener/session
```

If an app has multiple targets such as `pending-image`, `cover-template`, or `reference-image`, never determine the target later by querying whichever DOM element is selected after the upload finishes.

## Permissions

Declare only methods the final app calls. Current public examples use permission names such as:

```json
"permissions": [
  "phoneBridge.openPanel",
  "phoneBridge.createSession",
  "phoneBridge.receiveFiles",
  "phoneBridge.readFiles"
]
```

Optional output permissions:

```json
"permissions": [
  "phoneBridge.addFiles",
  "phoneBridge.sendToPhone"
]
```

Do not keep output permissions in an input-only app. A permission declaration does not create a Host API method; feature-detect the method at runtime.

## Resolve the bridge safely

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

Resolve the bridge when the user triggers the action. Do not cache a missing bridge forever.

## Receive flow

When the current host exposes `onFilesReceived` + `readFile`, treat the receive descriptor as metadata, not the file body. Read each `fileId`, normalize the returned Blob to a File, then reuse the app's normal file handler.

```js
const bridge = getBridge()
const phone = bridge?.phoneBridge

if (typeof phone?.onFilesReceived !== 'function' || typeof phone?.readFile !== 'function') {
  showDesktopPickerFallback()
  return
}

const unsubscribe = phone.onFilesReceived(async (items) => {
  for (const item of items) {
    const blob = await phone.readFile(item.fileId)
    const file = new File(
      [blob],
      item.name || `phone-${Date.now()}`,
      { type: blob.type || item.mimeType || 'application/octet-stream' }
    )
    await handleFile(file, 'phone-bridge')
  }
})
```

Do not put the descriptor directly into a business file list. Do not use a generic `window.message` listener as the primary receive channel. Save and call `unsubscribe` when the view is destroyed.

## Multiple-target intake

Capture a stable application target before opening the async phone flow:

```js
let pendingPhoneTarget = null

async function importFromPhone(targetId, purpose) {
  pendingPhoneTarget = { targetId, purpose }

  const phone = getBridge()?.phoneBridge
  if (!phone) {
    return openPickerForTarget(targetId)
  }

  // Subscribe/create the supported receive flow first.
  // Then open the host Phone Bridge UI/session.
}

async function applyPhoneFile(file, context = pendingPhoneTarget) {
  if (!context?.targetId) return
  const normalized = await normalizeInputFile(file)
  await applyFileToTarget(context.targetId, normalized, context.purpose)
}
```

The exact method set still depends on the running host. The public rule is more important than any example method name: **capture target → establish intake → open transfer UI → receive/read → normalize → apply to captured target**.

## Create a receive session

When the host exposes `createSession`, create it only after a user action and explain what the phone upload will be used for.

```js
const session = await phone.createSession({
  targetAppId: APP_ID,
  acceptTypes: ['image/*', 'application/pdf', 'text/plain'],
  maxFiles: 12
})
```

Treat returned QR/session fields as sensitive runtime data:

- render them only in the current UI when needed
- do not write them to logs, diagnostics, source files, analytics, or persistent storage
- when producing shareable diagnostics, keep only non-sensitive state such as `sessionCreated: true`

When the host exposes only a system panel flow, use that flow plus the supported application intake mechanism; do not invent a private file-path lookup.

## Add CEAPP output to Phone Bridge

When the running host exposes `addFile`, prefer Blob/File-style data and let the host manage transfer encoding.

```js
const record = await phone.addFile({
  name: 'result.png',
  mimeType: 'image/png',
  data: resultBlob,
  targetAppId: APP_ID,
  sourceAppName: 'Example App'
})
```

Do not convert large output to a data URL merely to pass it into Phone Bridge.

## Send existing Phone Bridge files to a phone

Only expose this action when the user can see which files will be sent and the host exposes the send method.

```js
await phone.sendToPhone({
  fileIds: selectedFileIds
})
```

## Unify file sources

Do not maintain a separate business pipeline for phone uploads. Picker, paste, browser drop, host-native drop, and Phone Bridge should converge before product logic:

```text
picker ───────┐
paste ────────┤
DOM drop ─────┤
host drop ────┼→ normalize/import → validate → preview → app state
Phone Bridge ─┘
```

This prevents one intake path from gaining validation/cropping/state behavior that another path accidentally skips.

## UX checklist

1. Explain why the phone flow is useful before opening it.
2. Keep a desktop picker fallback.
3. Show accepted types and file limits.
4. Capture a stable target ID before async transfer starts.
5. Display file name/type/size after the file is read, not a private desktop path.
6. Unsubscribe listeners when the app closes or the feature unmounts.
7. Show disabled, denied, expired-session, empty, receiving, success, and error states.
8. Never include live session details in copied diagnostics.
9. Verify the flow inside CanEngine; a Chrome-only success is insufficient.
