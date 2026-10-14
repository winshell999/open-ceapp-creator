# Form prefill source starter

Generate this template with `create_ceapp.py --profile form-prefill --url HTTPS_PAGE --mapping reviewed-request.json`. The raw template has no target or mapping and is intentionally not packageable. Use only synthetic fixture values in the reviewed JSON; never bundle real personal data.

Requires a CanEngine 1.8.0+ build containing `CanEngine.browser.prefill`, macOS 14+ or Windows amd64/WebView2, and host permission approval for the fixed page. The local stdlib backend serves an offline shell; the official website requires internet. User inputs go through the app's controlled Host Bridge in memory. This starter does not save profiles, log payloads, use URL parameters for data, or automatically submit.

Customize `assets/form-config.json`: `labels[key]` and `formatHints[key]` use zh-CN/en-US objects. `options[key]` is an array of `{value, label:{"zh-CN":"…","en-US":"…"}}`, using verified option values. The `request` follows the public prefill JSON schema. Replace fixture defaults with empty values for production. Keep a researched mapping and synthetic fixture in the acceptance materials outside the app package.

Click Prefill to open the declared website in CanEngine's right pane. Check field reports, review and edit on the website, complete its verification and submit yourself. Missing/changed/protected controls require manual handling. Unknown outcomes lock actions; inspect the website and previous operation before reopening and retrying.

This is source, not a signed CEAPP. Run structural checks, then sign/install through the authorized CanEngine flow and test the actual website with synthetic data. Browser simulation does not prove native acceptance. Windows native acceptance is a separate gate. If adding SQLite, preserve existing schemas, use CANENGINE_APP_DATA_DIR and authenticated/no-store local data routes; do not expose DB paths or full profiles in diagnostics.
