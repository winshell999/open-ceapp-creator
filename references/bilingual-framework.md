# Bilingual Framework

## Locale Targets

- Primary locales: `zh-CN`, `en-US`
- Normalize any `en*` input to `en-US`
- Normalize everything else to `zh-CN` unless the app has a better explicit rule

## Locale Priority

When the app is inside CanEngine:

1. host locale from `CanEngine.getLocale()`
2. app-local storage fallback
3. `navigator.language`
4. app default locale

When the app is standalone:

1. app-local storage
2. `navigator.language`
3. app default locale

## Host Bridge Contract

Treat locale calls as potentially asynchronous:

- `getLocale(): string | Promise<string>`
- `setLocale(locale: string): string | Promise<string>`
- `onLocaleChange(handler): unsubscribe | void`

Do not pass the raw return value of `getLocale()` directly into string normalization unless you have confirmed it is not a Promise.

A robust startup pattern is:

1. render immediately from local storage / `navigator.language` so the first screen is not blocked;
2. resolve `await CanEngine.getLocale()` when the bridge is available;
3. apply the host locale when it arrives;
4. subscribe once to future host locale changes;
5. unsubscribe when the application/view is disposed.

The bundled `assets/starter/assets/ceapp-i18n.js` follows this pattern.

The CEAPP should also:

- update `document.documentElement.lang`
- re-render visible copy when locale changes
- localize document title, labels, placeholders, empty/error states, image alt text, and accessible names
- avoid showing a duplicate language toggle unless changing platform language is the requested feature

## Message Table Shape

Recommended shape:

```js
const messages = {
  'zh-CN': {
    'app.title': '示例应用',
    'action.run': '开始执行'
  },
  'en-US': {
    'app.title': 'Example App',
    'action.run': 'Run'
  }
}
```

## Rendering Rules

- Keep a single `t()` function close to the app root.
- Do not translate command IDs, API flags, filenames, or machine-facing values.
- Translate UI copy, hints, empty states, modal text, menu labels, status labels, and error copy shown to users.
- Keep the `zh-CN` and `en-US` key sets identical. Treat a missing translation as a validation failure, not a fallback strategy.
- Dynamic strings should use interpolation:

```js
t('result.count', { count: 4 })
```

## App Metadata

For app cards shown by CanEngine, include localized metadata in `app.json` when supported:

```json
{
  "nameI18n": {
    "zh-CN": "示例应用",
    "en-US": "Example App"
  },
  "descriptionI18n": {
    "zh-CN": "离线优先的双语示例应用。",
    "en-US": "An offline-first bilingual example app."
  }
}
```

Keep `name` and `description` as safe defaults, but do not rely on host-side fallback tables when manifest metadata can carry the translations.

## Current Product Direction

The current CanEngine platform owns locale state and exposes a Host Bridge for it. New apps should usually:

- follow host locale automatically
- keep standalone fallback behavior
- keep bilingual message tables local
- avoid adding extra locale controls by default

Only add an in-app language toggle for demos, settings tools, or apps where changing the platform language is the requested feature.

## Verification

1. Start in `zh-CN`, exercise every empty/loading/success/error state, and inspect the document title and accessible labels.
2. Change the CanEngine platform language to `en-US` while the app remains open.
3. Confirm visible copy rerenders without reloading or losing user input.
4. Repeat in standalone browser mode with `navigator.language` or the app-local fallback.
5. Search for user-facing string literals outside the message tables and either localize or justify them.
