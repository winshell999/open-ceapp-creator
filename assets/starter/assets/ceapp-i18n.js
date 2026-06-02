(function initCanEngineAppI18n(global) {
  const SUPPORTED = ['zh-CN', 'en-US'];

  function normalizeLocale(input) {
    const value = String(input || '').trim().toLowerCase();
    if (value.startsWith('en')) return 'en-US';
    return 'zh-CN';
  }

  function getBridge() {
    return global.CanEngine || (global.parent && global.parent.CanEngine) || null;
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

    try {
      const bridge = getBridge();
      locale = normalizeLocale(
        bridge?.getLocale?.() ||
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
      syncDocumentLanguage();
      listeners.forEach((listener) => {
        try {
          listener(locale);
        } catch {
          // ignore listener errors from app consumers
        }
      });
    }

    function setLocale(nextLocale, options = {}) {
      const resolved = normalizeLocale(nextLocale);
      locale = resolved;
      try {
        global.localStorage?.setItem(storageKey, resolved);
      } catch {
        // ignore storage failures
      }
      if (options.propagate !== false) {
        try {
          getBridge()?.setLocale?.(resolved);
        } catch {
          // ignore bridge propagation failures
        }
      }
      notify();
      return locale;
    }

    try {
      const bridge = getBridge();
      if (bridge?.onLocaleChange) {
        hostUnsubscribe = bridge.onLocaleChange((nextLocale) => {
          setLocale(nextLocale, { propagate: false });
        });
      }
    } catch {
      hostUnsubscribe = null;
    }

    syncDocumentLanguage();

    return {
      appId,
      getLocale() {
        return locale;
      },
      setLocale,
      subscribe(listener) {
        if (typeof listener !== 'function') return () => {};
        listeners.add(listener);
        listener(locale);
        return () => {
          listeners.delete(listener);
        };
      },
      dispose() {
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
