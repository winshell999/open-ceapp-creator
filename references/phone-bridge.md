# Phone Bridge

Use the host Phone Bridge, not a CEAPP-owned LAN server, cloud relay or hardcoded IP.

## Full demonstration

1. Open Phone Bridge workbench, or Create session.
2. Create session subscribes to received files first, then calls createSession({targetAppId,acceptTypes,maxFiles}) and opens the host panel for its authoritative QR UI.
3. Scan using a real connected phone and send a permitted sample file.
4. Receive callbacks hold Phone Bridge file records with fileId.
5. Import received file calls readFile(fileId), obtains Blob, stages it with the app ID, and produces a StagedFile.id usable for Python.
6. Add sample puts a small Blob into the workbench via addFile.
7. Send sample calls sendToPhone({fileIds}) only after the app confirmation.

The callback is installed only for an intentional session, not at startup. Each app view owns and removes its subscription. Callback exceptions are contained.
Session data is not printed or exported by the Lab. The host panel handles QR presentation/renewal; do not attempt to render a qrUrl as an image or persist an expired token.

## Public methods

openPanel(), createSession(request), onFilesReceived(handler), readFile(fileId), addFile({name,mimeType,data,targetAppId}), sendToPhone({fileIds}).
Permissions map respectively to phoneBridge.openPanel/createSession/receiveFiles/readFiles/addFiles/sendToPhone.
Use only the permissions actually exercised. `requireUserConfirm` is not consumed by the inspected send wrapper and therefore is not a security control.

## Limits and failure states

The Lab caps Blob/base64 imports at 8 MiB. For larger inputs use the host workbench or a future documented streaming API; do not allocate unbounded base64 buffers.
Distinguish no phone connected, bridge disabled, CEAPP access disabled, permission denied, session expired, file removed and network interruption.
Canceling or closing the CEAPP does not imply a host-owned session is deleted. No session-delete method is exposed in the inspected JS contract; do not invent one.
Never count a mocked callback as device acceptance. Native testing must include a real phone, reverse send, expired session and duplicate filename.
