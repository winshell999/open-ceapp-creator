# Offline and runtime strategy

The Lab is hybrid-online: first paint and local file preview are local; AI/phone/website operations need configured capabilities and potentially a network. Do not claim that all its features work offline.
All runtime HTML/CSS/JS/icons reside in the package. No CDN, external stylesheet, web font, remote React or build-time server is needed to display the shell.
The starter uses ordinary scripts in a deterministic order. Do not ship unbundled module imports and assume the host's HTML preparation resolves them. If a framework is genuinely needed, ship a local built bundle and test installation and native asset rewriting.

Use assetURL(appId,path) for normal package media. Use assetDataURL for deliberately small copy/inline operations. Large video/audio should never be base64-copied into UI memory simply for convenience.
Host native drop and DOM drop are distinct. The starter avoids duplicate processing by preferring native onFileDrop when installed, while retaining DOM drop/paste for browser preview. Test the actual target WebView's behavior.

Native targets remain distinct: macOS WebKit/WKWebView and Windows WebView2/Chromium. Chromium test fixtures do not prove WKWebView compatibility. Browser file:// loading and installed package routing are separate acceptance items.
Keep node_modules/tests/backups/archives/signing secrets/runtime caches outside the CEAPP source root. Use scripts/validate_ceapp.py before packaging.
