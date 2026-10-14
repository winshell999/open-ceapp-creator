# Troubleshooting by evidence

| Symptom | Check first | Do not do |
|---|---|---|
| Works in browser, blank in host | Actual installed entry, local script/style paths, prepared HTML, missing globals | Add a remote CDN or assume preview PASS proves installation |
| CanEngine undefined | Delayed injection, app scope, guarded parent access, actual installed context | Dereference parent unguarded or fabricate results |
| Open website fails | openExternalURL availability, normalized HTTP(S), host error | Guess openURL/openExternal or use Wails directly |
| File opens but Python sees nothing | StagedFile.id in inputFileIds; current appId | Pass filename, phone fileId or bare path as input ID |
| Cancel never available | Subscribe to full job:started before blocking runJob | Await the final JobInfo first |
| Wrong task cancelled | Match appId, commandId, current job ID, unique active ownership | Use the first broadcast job ID |
| Python argparse error | Runner-owned -i/-o/--result-json, declared flags | Duplicate runner flags or shell-interpolate inputs |
| Task says success, no output | Actual result JSON files, on-disk existence, result envelope | Invent fileRef/path or create fake success |
| Python not found | requireRuntime.ok, managed runtime status | Assume system PATH or auto-install packages |
| AI request fails | Feature declaration, permission, host configuration, provider result | Ask for a key inside the app or silently use another service |
| Video permission mismatch | Method ai.video.create versus permission ai.video.generate | Use ai.video.generate as a method |
| Database unavailable | Local schema, factory API, exact shared resource ID, grant | Guess dataset IDs or raw shared SQL |
| Phone file cannot process | readFile -> Blob -> stageFile -> staged.id | Reuse phone fileId as a job input |
| QR expired/no phone | Host session/workbench, connectivity, CEAPP allowance | Persist/print QR tokens or invent session APIs |
| Repeated charge/duplicate output | In-flight/unknown lock, late-result reconciliation, host history | Automatically retry a timeout |
| Notification reappears after deletion | Registration only on explicit save; tombstones | Register/reactivate at startup |
| Copy/print wrong content type | Distinguish text, pixel image, file, HTML | Treat clipboard and save-file APIs as interchangeable |

Collect appId, host version, method name, safe error code, verified task ID, platform and a minimal reproducible fixture. Never collect API keys, session tokens or whole private chats just for debugging.
