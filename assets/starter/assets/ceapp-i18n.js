(function initCanEngineAppI18n(global) {
  const SUPPORTED = ['zh-CN', 'en-US'];

  function normalizeLocale(input) {
    const value = String(input || '').trim().toLowerCase();
    if (value.startsWith('en')) return 'en-US';
    return 'zh-CN';
  }

  function getBridge() {
    try {
      if (global.CanEngine) return global.CanEngine;
    } catch {
      // Ignore host access failures and keep standalone fallback usable.
    }

    try {
      if (global.parent && global.parent !== global && global.parent.CanEngine) {
        return global.parent.CanEngine;
      }
    } catch {
      // A cross-origin parent may reject property access in browser debugging.
    }

    return null;
  }

  function interpolate(template, vars) {
    return Object.entries(vars || {}).reduce((output, [key, value]) => {
      return output.replaceAll(`{${key}}`, String(value));
    }, template);
  }

  function createI18n(options) {
    const appId = options?.appId || 'ceapp';
    const defaultLocale = normalizeLocale(options?.defaultLocale || 'zh-CN');
    const messages = options?.messages || {};
    const storageKey = `canengine.app.locale.${appId}`;
    const listeners = new Set();

    let locale = defaultLocale;
    let hostUnsubscribe = null;
    let disposed = false;

    try {
      locale = normalizeLocale(
        global.localStorage?.getItem(storageKey) ||
        global.navigator?.language ||
        defaultLocale
      );
    } catch {
      locale = defaultLocale;
    }

    function syncDocumentLanguage() {
      if (global.document?.documentElement) {
        global.document.documentElement.lang = locale;
      }
    }

    function notify() {
      if (disposed) return;
      syncDocumentLanguage();
      listeners.forEach((listener) => {
        try {
          listener(locale);
        } catch {
          // Ignore listener errors from app consumers.
        }
      });
    }

    function applyLocale(nextLocale, { persist = true } = {}) {
      if (disposed) return locale;
      const resolved = normalizeLocale(nextLocale);
      const changed = resolved !== locale;
      locale = resolved;

      if (persist) {
        try {
          global.localStorage?.setItem(storageKey, resolved);
        } catch {
          // Ignore storage failures.
        }
      }

      if (changed) notify();
      else syncDocumentLanguage();
      return locale;
    }

    function setLocale(nextLocale, options = {}) {
      const resolved = applyLocale(nextLocale);

      if (options.propagate !== false) {
        try {
          const result = getBridge()?.setLocale?.(resolved);
          if (result && typeof result.catch === 'function') {
            result.catch(() => {});
          }
        } catch {
          // Ignore bridge propagation failures; local locale still works.
        }
      }

      return locale;
    }

    async function syncHostLocale() {
      const bridge = getBridge();
      if (!bridge?.getLocale) return;

      try {
        const hostLocale = await bridge.getLocale();
        if (!disposed && hostLocale) {
          applyLocale(hostLocale);
        }
      } catch {
        // Keep app/browser fallback locale.
      }
    }

    try {
      const bridge = getBridge();
      if (bridge?.onLocaleChange) {
        const maybeUnsubscribe = bridge.onLocaleChange((nextLocale) => {
          applyLocale(nextLocale);
        });
        if (typeof maybeUnsubscribe === 'function') {
          hostUnsubscribe = maybeUnsubscribe;
        }
      }
    } catch {
      hostUnsubscribe = null;
    }

    syncDocumentLanguage();
    void syncHostLocale();

    return {
      appId,
      getLocale() {
        return locale;
      },
      setLocale,
      refreshFromHost() {
        return syncHostLocale();
      },
      subscribe(listener) {
        if (typeof listener !== 'function') return () => {};
        listeners.add(listener);
        listener(locale);
        return () => {
          listeners.delete(listener);
        };
      },
      dispose() {
        disposed = true;
        if (typeof hostUnsubscribe === 'function') {
          hostUnsubscribe();
        }
        listeners.clear();
      },
      t(key, vars = {}) {
        const table = messages[locale] || {};
        const fallback = messages['zh-CN'] || {};
        const template = table[key] ?? fallback[key] ?? key;
        return interpolate(template, vars);
      },
      supportedLocales() {
        return SUPPORTED.slice();
      }
    };
  }

  global.CanEngineAppI18n = {
    createI18n,
    normalizeLocale,
    supportedLocales() {
      return SUPPORTED.slice();
    }
  };
})(window);
