# Bilingual framework

Use zh-CN and en-US. Normalize en* to en-US and other values to the app's explicit default (zh-CN in this Lab).
Priority: successful host getLocale -> saved app locale -> navigator language -> default. Catch storage exceptions and host failures; locale must never blank the UI.
Subscribe once to onLocaleChange, update document.lang/title/visible labels, and unsubscribe on disposal. Do not trigger host locale changes merely to initialize the app. The Lab intentionally offers a language control for acceptance; normal apps usually follow the host without an extra switch.
Keep all user-facing labels and common error recovery messages in the central table. Retain machine IDs, flags, method names and status codes untranslated in technical details.

## Helper migration

The refactored helper exposes `CEI18n.create()` with get/set/t. The app uses it directly; old starter-specific helper names are not a compatibility promise. When migrating an older CEAPP, update the helper and callers together, and keep any additional business translations.
The Node suite verifies exact English/Chinese key parity. Changing the app name also requires updating title translations and manifest metadata; do not leave the demo title in a finished business app.
