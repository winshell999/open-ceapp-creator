# Bilingual Framework

## Locale Targets

- Primary locales: `zh-CN`, `en-US`
- Normalize any `en*` input to `en-US`
- Normalize everything else to `zh-CN` unless the app has a better explicit rule

## Locale Priority

When the app is inside CanEngine:

1. `CanEngine.getLocale()`
2. app-local storage fallback
3. `navigator.language`
4. app default locale

When the app is standalone:

1. app-local storage
2. `navigator.language`
3. app default locale

## Host Bridge Contract

CanEngine should expose:

- `getLocale(): string`
- `setLocale(locale: string): string | Promise<string>`
- `onLocaleChange(handler): unsubscribe`

The ceapp should:

- subscribe once on startup
- update `document.documentElement.lang`
- re-render visible copy when locale changes
- avoid showing a duplicate language toggle unless the user explicitly wants local override UX

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

Keep `name` and `description` as safe defaults, but do not rely on host-side fallback tables for first-party apps when manifest metadata can carry the translations.

## Current Product Direction

The current CanEngine platform already owns locale state and exposes a host bridge for it. New apps should usually:

- follow host locale automatically
- keep standalone fallback behavior
- keep bilingual message tables local
- avoid adding extra locale controls by default

Only add an in-app language toggle for demos, settings tools, or apps where changing the platform language is the requested feature.
