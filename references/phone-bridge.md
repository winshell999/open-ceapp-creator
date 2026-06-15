# Phone Bridge For Public CEAPP Source

Use CanEngine Phone Bridge when a CEAPP needs users to send files, images, text, or links from a phone into the desktop host without shipping a custom mobile app or a cloud relay.

## Public-Safe Positioning

- Phone Bridge is a CanEngine system capability, not a CEAPP-owned server.
- The CEAPP should call `window.CanEngine.phoneBridge`, not open its own LAN listener.
- Public CEAPP source must not hard-code private LAN addresses, session tokens, desktop file paths, or internal debugging endpoints.
- Phone Bridge support should degrade gracefully when the app is opened in a normal browser outside CanEngine.

## Recommended Bridge Surface

Prefer these APIs when available:

```text
window.CanEngine.phoneBridge.openPanel()
window.CanEngine.phoneBridge.createSession(request)
window.CanEngine.phoneBridge.onFilesReceived(handler)
window.CanEngine.phoneBridge.readFile(fileId)
window.CanEngine.phoneBridge.addFile(request)
window.CanEngine.phoneBridge.sendToPhone(request)
```

## Typical CEAPP Flow

1. The app asks CanEngine to create a Phone Bridge session.
2. CanEngine returns a QR session descriptor.
3. The CEAPP displays the returned QR information in its own UI, or asks the host to open the system Phone Bridge panel.
4. The user scans from a phone and uploads files.
5. CanEngine stores those files in the Phone Bridge workspace and notifies the target CEAPP.
6. The CEAPP reads the received file by `fileId`, then continues its normal business flow.

## Session Example

```js
const session = await window.CanEngine.phoneBridge.createSession({
  targetAppId: "your-app-id",
  acceptTypes: ["image/*", "application/pdf", "text/plain"],
  maxFiles: 12
});
```

Expected session shape:

```js
{
  sessionId: "pb_sess_xxx",
  qrUrl: "http://<local-ip>:<port>/mobile?sid=...&token=...",
  qrDataUrl: "data:image/png;base64,...",
  expiresAt: 1791870000
}
```

## Receive Flow Example

```js
const unsubscribe = window.CanEngine.phoneBridge.onFilesReceived(async (files) => {
  for (const file of files) {
    const blob = await window.CanEngine.phoneBridge.readFile(file.fileId);
    // Continue app-specific processing here.
  }
});
```

## Add App Output Back Into Phone Bridge

Use `addFile()` when the CEAPP creates a file that should appear in the system Phone Bridge workspace.

```js
await window.CanEngine.phoneBridge.addFile({
  name: "poster.png",
  mimeType: "image/png",
  data: blob,
  targetAppId: "your-app-id"
});
```

## Send File Back To Phone

Only request this when the user can reasonably understand what is being sent.

```js
await window.CanEngine.phoneBridge.sendToPhone({
  fileIds: ["file_xxx"],
  requireUserConfirm: false
});
```

## Permission Guidance

For current public CEAPP source, prefer flat string permissions in `app.json`:

```json
[
  "phoneBridge.openPanel",
  "phoneBridge.createSession",
  "phoneBridge.receiveFiles",
  "phoneBridge.readFiles",
  "phoneBridge.addFiles",
  "phoneBridge.sendToPhone"
]
```

Remove permissions that the app does not actually need before shipping.

## UX Guidance

- Explain why the app is opening Phone Bridge or asking for a QR session.
- Treat Phone Bridge as a focused sub-flow, not the whole app.
- Keep a fallback path such as normal file picker when possible.
- When showing a QR block inside the CEAPP, also show a text explanation of what the phone upload is for.

## Good Public Reference

- `Apps/demo/` in the CanEngine workspace is the current feature-rich CEAPP example for Phone Bridge, AI Bridge, assets, jobs, and file staging.

## Do Not Do This

- Do not expose desktop absolute paths in CEAPP UI as the primary contract.
- Do not ask CEAPP authors to create their own upload web server for routine phone intake.
- Do not commit private publisher IDs, signing secrets, trusted key IDs, local Wi-Fi details, or internal API base URLs into public starter code.
