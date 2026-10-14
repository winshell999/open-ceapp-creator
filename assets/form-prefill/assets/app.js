(() => {
  'use strict';
  const status = document.getElementById('status');
  const report = document.getElementById('report');
  const prefill = document.getElementById('prefill');
  const open = document.getElementById('open');
  const controls = new Map();
  let config = null, host = null, busy = false, unresolved = false, disposed = false;
  let locale = 'zh-CN', statusKey = 'preparing', fieldResults = [], unsubscribe = null;
  const copy = key => window.PREFILL_COPY[locale][key] || key;
  const localized = value => typeof value === 'string' ? value : value?.[locale] || value?.['en-US'] || '';
  function message(key) { statusKey = key; status.textContent = copy(key); }
  function buttons() { prefill.disabled = open.disabled = !config || !host || busy || unresolved; }
  function paintReport() {
    report.replaceChildren();
    const known = new Set(['available','filled','missing','ambiguous','blocked','protected','option-missing','mismatch','invalid']);
    for (const result of fieldResults) {
      if (!controls.has(result.field) || !known.has(result.status)) continue;
      const item = document.createElement('li');
      item.textContent = (localized(config.labels[result.field]) || result.field) + ': ' + copy(result.status === 'invalid' ? 'invalidField' : result.status);
      report.append(item);
    }
  }
  function language(value) {
    locale = value === 'en-US' ? 'en-US' : 'zh-CN';
    document.documentElement.lang = locale;
    document.title = document.getElementById('title').textContent = localized(config?.titleI18n) || copy('prefill');
    document.querySelectorAll('[data-i18n]').forEach(node => { node.textContent = copy(node.dataset.i18n); });
    for (const [key, control] of controls) {
      control.label.textContent = localized(config.labels[key]) || key;
      control.hint.textContent = localized(config.formatHints[key]);
      if (control.input.tagName === 'SELECT') {
        for (const option of control.input.options) option.textContent = localized(option._label) || option.value;
      }
    }
    message(statusKey); paintReport();
  }
  function fields() {
    const container = document.getElementById('fields');
    container.replaceChildren();
    for (const field of config.request.fields) {
      const wrapper = document.createElement('label'); wrapper.className = 'field';
      const label = document.createElement('span'), hint = document.createElement('small');
      const options = config.options[field.key];
      const input = document.createElement(field.kind === 'textarea' ? 'textarea' : field.kind === 'select' && Array.isArray(options) ? 'select' : 'input');
      const toggle = field.kind === 'checkbox' || field.kind === 'radio';
      if (input.tagName === 'INPUT') input.type = toggle ? 'checkbox' : field.kind === 'select' ? 'text' : field.kind;
      input.autocomplete = 'off'; input.name = field.key;
      if (input.tagName === 'SELECT') {
        for (const option of options) {
          const node = document.createElement('option'); node.value = option.value; node._label = option.label; input.append(node);
        }
      }
      if (toggle) input.checked = field.value; else input.value = field.value;
      wrapper.append(label, input, hint); container.append(wrapper);
      controls.set(field.key, {input, label, hint, toggle});
    }
  }
  function request() {
    return {...config.request, fields:config.request.fields.map(field => {
      const control = controls.get(field.key);
      return {...field, value:control.toggle ? control.input.checked : control.input.value};
    })};
  }
  async function act(fill) {
    if (!host || !config || busy || unresolved || disposed) return;
    busy = true; fieldResults = []; paintReport(); buttons(); message('loading');
    let payload = null;
    try {
      payload = fill ? request() : null;
      const result = fill ? await host.browser.prefill(payload) : await host.browser.openTarget(config.request.target);
      if (disposed) return;
      if (fill) {
        if (!result || typeof result.ok !== 'boolean' || !Array.isArray(result.fields) || result.manualRequired !== true) {
          unresolved = true; message('unknown');
        } else {
          fieldResults = result.fields; paintReport(); message(result.ok ? 'review' : 'manual');
        }
      } else message(result?.open === true ? 'opened' : 'failed');
    } catch (error) {
      if (disposed) return;
      // Only a known terminal host error permits another user-triggered action.
      const code = String(error?.message || '').match(/\bBROWSER_[A-Z_]+\b/)?.[0];
      const terminal = new Set(['BROWSER_PERMISSION_DENIED','BROWSER_TARGET_DENIED','BROWSER_PAYLOAD_INVALID','BROWSER_PROFILE_DENIED','BROWSER_OWNER_CLOSED','BROWSER_DOMAIN_DENIED','BROWSER_NAVIGATION_CHANGED','BROWSER_OPERATION_TIMEOUT','BROWSER_SUBMISSION_BLOCKED','BROWSER_LOAD_FAILED','BROWSER_LOAD_TIMEOUT','BROWSER_OPERATION_FAILED']);
      unresolved = !terminal.has(code); message(unresolved ? 'unknown' : 'failed');
    } finally {
      payload = null; busy = false; buttons();
    }
  }
  prefill.addEventListener('click', () => { void act(true); });
  open.addEventListener('click', () => { void act(false); });
  window.addEventListener('pagehide', () => {
    disposed = true; if (typeof unsubscribe === 'function') unsubscribe();
    config = null; host = null; fieldResults = []; controls.clear();
  }, {once:true});
  async function start() {
    try {
      const response = await fetch('/assets/form-config.json', {cache:'no-store'});
      if (!response.ok) throw new Error('CONFIG');
      config = await response.json();
      if (!config?.request || !Array.isArray(config.request.fields) || !config.request.fields.length) throw new Error('CONFIG');
      config.labels ||= {}; config.options ||= {}; config.formatHints ||= {};
      fields(); language(navigator.language.startsWith('en') ? 'en-US' : 'zh-CN');
    } catch { config = null; message('invalid'); return; }
    const deadline = Date.now() + 4000;
    while (!disposed && Date.now() < deadline) {
      const candidate = window.CanEngine;
      if (typeof candidate?.browser?.prefill === 'function' && typeof candidate?.browser?.openTarget === 'function') { host = candidate; break; }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (disposed) return;
    if (!host) { message('hostMissing'); return; }
    if (typeof host.onLocaleChange === 'function') unsubscribe = host.onLocaleChange(language);
    if (typeof host.getLocale === 'function') {
      try { language(await host.getLocale()); } catch { /* Keep the visible local fallback. */ }
    }
    message('ready'); buttons();
  }
  void start();
})();
