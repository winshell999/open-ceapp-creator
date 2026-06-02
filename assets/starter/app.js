const APP_ID = 'starter-app'

const messages = {
  'zh-CN': {
    'app.title': 'Starter App',
    'app.subtitle': '一个可离线打开、可跟随平台语言的 ceapp 模板。',
    'panel.title': '欢迎',
    'panel.body': '从这里开始替换成你的真实应用界面。这个 starter 已经具备本地资产、语言同步和独立运行回退能力。',
    'panel.action': '开始使用',
    'ai.title': 'AI桥示例',
    'ai.body': '这是可复制的最小 AI桥用法。API Key 保存在宿主，ceapp 只声明能力并调用 window.CanEngine.ai。',
    'ai.prompt': '请用一句话介绍这个 ceapp 模板。',
    'ai.text': '生成文本',
    'ai.status': '读取状态',
    'ai.ready': '等待操作...',
    'ai.missing': '当前宿主没有暴露 AI桥。'
  },
  'en-US': {
    'app.title': 'Starter App',
    'app.subtitle': 'An offline-ready ceapp template that follows the platform locale.',
    'panel.title': 'Welcome',
    'panel.body': 'Replace this with your real application UI. This starter already includes local assets, locale sync, and standalone fallback behavior.',
    'panel.action': 'Get Started',
    'ai.title': 'AI Bridge Example',
    'ai.body': 'A minimal AI Bridge usage sample. API keys stay in the host; the ceapp only declares capabilities and calls window.CanEngine.ai.',
    'ai.prompt': 'Introduce this ceapp template in one sentence.',
    'ai.text': 'Generate Text',
    'ai.status': 'Read Status',
    'ai.ready': 'Waiting for action...',
    'ai.missing': 'The current host does not expose AI Bridge.'
  }
}

const i18n = window.CanEngineAppI18n.createI18n({
  appId: APP_ID,
  defaultLocale: 'zh-CN',
  messages
})

async function resolvePackagedAsset(assetPath) {
  const bridge = getBridge()

  try {
    if (bridge?.assetURL) {
      return await bridge.assetURL(APP_ID, assetPath)
    }
  } catch (error) {
    console.warn('assetURL failed, falling back', error)
  }

  try {
    if (bridge?.assetDataURL) {
      return await bridge.assetDataURL(APP_ID, assetPath)
    }
  } catch (error) {
    console.warn('assetDataURL failed, falling back', error)
  }

  return assetPath
}

async function hydrateAssets() {
  const logo = document.getElementById('app-logo')
  if (!logo) return
  logo.src = await resolvePackagedAsset('assets/logo.png')
}

function getBridge() {
  return window.CanEngine || (window.parent && window.parent.CanEngine) || null
}

function setAIOutput(value) {
  const output = document.getElementById('ai-output')
  if (!output) return
  output.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

async function readAIStatus() {
  const bridge = getBridge()
  if (!bridge?.ai?.getStatus) {
    setAIOutput(i18n.t('ai.missing'))
    return
  }
  try {
    setAIOutput(await bridge.ai.getStatus())
  } catch (error) {
    setAIOutput(error?.message || String(error))
  }
}

async function generateAIText() {
  const bridge = getBridge()
  if (!bridge?.ai?.text?.generate) {
    setAIOutput(i18n.t('ai.missing'))
    return
  }
  const prompt = document.getElementById('ai-prompt').value.trim() || i18n.t('ai.prompt')
  try {
    const response = await bridge.ai.text.generate({
      messages: [{ role: 'user', content: prompt }],
      maxTokens: 240
    })
    setAIOutput(response)
  } catch (error) {
    setAIOutput(error?.message || String(error))
  }
}

function render() {
  const locale = i18n.getLocale()
  const t = (key) => i18n.t(key)

  document.title = t('app.title')
  document.documentElement.lang = locale
  document.getElementById('app-title').textContent = t('app.title')
  document.getElementById('app-subtitle').textContent = t('app.subtitle')
  document.getElementById('panel-title').textContent = t('panel.title')
  document.getElementById('panel-body').textContent = t('panel.body')
  document.getElementById('primary-action').textContent = t('panel.action')
  document.getElementById('ai-title').textContent = t('ai.title')
  document.getElementById('ai-body').textContent = t('ai.body')
  document.getElementById('ai-prompt').placeholder = t('ai.prompt')
  document.getElementById('ai-text-action').textContent = t('ai.text')
  document.getElementById('ai-status-action').textContent = t('ai.status')
}

document.getElementById('ai-text-action')?.addEventListener('click', generateAIText)
document.getElementById('ai-status-action')?.addEventListener('click', readAIStatus)
setAIOutput(messages['zh-CN']['ai.ready'])
hydrateAssets()
i18n.subscribe(render)
