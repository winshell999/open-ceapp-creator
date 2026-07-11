# Phone Bridge for Public CEAPP Source

Use Phone Bridge when users need to move files from a phone into a desktop CEAPP or explicitly send CEAPP output back to a phone. Keep a normal file picker fallback whenever possible.

## Public-safe boundary

- Phone Bridge is a CanEngine system capability, not a CEAPP-owned server.
- Call `window.CanEngine.phoneBridge`; do not create a custom LAN listener.
- Never log or publish QR payloads, session URLs, tokens, private IP addresses, or desktop paths.
- Do not persist a session descriptor. Create a new short-lived session when the user asks.
- Degrade to a picker or clear unavailable state outside CanEngine.

## Permissions

Declare only methods the final app calls:

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

Do not keep output permissions in an input-only app.

## Receive flow

The descriptor from `onFilesReceived` is metadata, not the file body. Read each `fileId`, normalize the returned Blob to a File, then reuse the app's normal file handler.

```js
const bridge = window.CanEngine || (window.parent && window.parent.CanEngine)

const unsubscribe = bridge.phoneBridge.onFilesReceived(async (items) => {
  for (const item of items) {
    const blob = await bridge.phoneBridge.readFile(item.fileId)
    const file = new File(
      [blob],
      item.name || `phone-${Date.now()}`,
      { type: blob.type || item.mimeType || 'application/octet-stream' }
    )
    await handleFile(file, 'phone-bridge')
  }
})
```

Do not put the descriptor directly into a business file list. Do not use a generic `window.message` listener as the primary receive channel.

## Create a receive session

Create a session only after a user action and explain what the phone upload will be used for.

```js
const session = await bridge.phoneBridge.createSession({
  targetAppId: APP_ID,
  acceptTypes: ['image/*', 'application/pdf', 'text/plain'],
  maxFiles: 12
})
```

Treat the returned QR/session fields as sensitive runtime data:

- render the QR only in the current UI when needed
- do not write it to logs, diagnostics, source files, analytics, or persistent storage
- when producing shareable diagnostics, keep only a boolean such as `sessionCreated: true`

`openPanel()` is the simplest path when the system Phone Bridge UI already explains the workflow.

## Add CEAPP output to Phone Bridge

Use a Blob or File. The host handles transfer encoding.

```js
const record = await bridge.phoneBridge.addFile({
  name: 'result.png',
  mimeType: 'image/png',
  data: resultBlob,
  targetAppId: APP_ID,
  sourceAppName: 'Example App'
})
```

Do not convert large output to a data URL in app code before calling `addFile`.

## Send existing Phone Bridge files to a phone

Only expose this action when the user can see which files will be sent.

```js
await bridge.phoneBridge.sendToPhone({
  fileIds: selectedFileIds
})
```

## UX checklist

1. Explain why the phone flow is useful before opening it.
2. Keep a desktop picker fallback.
3. Show accepted types and file limits.
4. Display file name/type/size after `readFile`, not a private desktop path.
5. Unsubscribe the listener when the app closes or the feature unmounts.
6. Show disabled, denied, expired-session, empty, receiving, success, and error states.
7. Never include live session details in copied diagnostics.
