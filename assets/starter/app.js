const APP_ID = 'starter-app'
const DEMO_NOTIFICATION_FEATURE_ID = 'starter-daily-brief'

const messages = {
  'zh-CN': {
    'app.title': 'Starter App',
    'app.subtitle': '一个可离线打开、可跟随平台语言的 ceapp 模板。',
    'panel.title': '欢迎',
    'panel.body': '从这里开始替换成你的真实应用界面。这个 starter 已经具备本地资产、语言同步、AI桥最小示例，以及通知桥的应用侧注册与即时发送示例。',
    'panel.action': '开始使用',
    'notification.title': '通知桥示例',
    'notification.body': '演示应用主动注册通知功能、读取桥侧治理状态、直接 send() 发送即时通知，以及应用侧关闭或删除后功能立即失效。',
    'notification.refresh': '刷新状态',
    'notification.openSettings': '打开通知桥设置',
    'notification.register': '注册/保存功能',
    'notification.toggle': '切换应用侧开关',
    'notification.sendDirect': '即时 send()',
    'notification.sendFeature': '按功能发送',
    'notification.delete': '应用侧删除',
    'notification.rulesTitle': '最小规则',
    'notification.rules.appOwned': '持久通知功能必须由应用主动注册，不能在通知桥里从零创建。',
    'notification.rules.dualState': '来源端开关、桥侧开关、全局通知桥和权限任一关闭，最终状态都会失效。',
    'notification.rules.delete': '桥侧删除不会自动恢复；只有应用再次显式保存或开启，注册项才会重建。',
    'notification.statusReady': '等待读取通知桥状态...',
    'notification.featureReady': '等待应用注册通知功能...',
    'notification.actionReady': '等待调用通知桥 API...',
    'notification.featureName': 'Starter 定时提醒',
    'notification.featureMissing': '请先从应用里注册这个通知功能',
    'notification.registered': '通知功能已注册/保存',
    'notification.toggled': '应用侧开关已更新',
    'notification.directSent': '已发送即时通知',
    'notification.featureSent': '已按功能发送一次通知',
    'notification.deleted': '通知功能已从应用侧删除',
    'notification.directTitle': 'Starter 即时通知',
    'notification.directContent': '这是一条由 starter ceapp 运行时直接发起的即时通知。时间：{time}',
    'notification.featureTitle': 'Starter 功能通知',
    'notification.featureContent': '这是一条依附已注册功能发送的通知。时间：{time}',
    'notification.missing': '当前宿主没有暴露通知桥。',
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
    'panel.body': 'Replace this with your real application UI. This starter already includes local assets, locale sync, a minimal AI Bridge sample, and Notification Bridge examples for app-owned registration plus direct send.',
    'panel.action': 'Get Started',
    'notification.title': 'Notification Bridge Example',
    'notification.body': 'Demonstrates app-initiated feature registration, bridge-side governance status, direct runtime send(), and immediate invalidation after the app disables or deletes a feature.',
    'notification.refresh': 'Refresh Status',
    'notification.openSettings': 'Open Bridge Settings',
    'notification.register': 'Register or Save',
    'notification.toggle': 'Toggle App Switch',
    'notification.sendDirect': 'Direct send()',
    'notification.sendFeature': 'Send With Feature',
    'notification.delete': 'Delete From App',
    'notification.rulesTitle': 'Minimal rules',
    'notification.rules.appOwned': 'Persistent notification features must be registered by the app, not created from scratch in the bridge.',
    'notification.rules.dualState': 'If source-side, bridge-side, global bridge, or permission is turned off, the effective state becomes inactive.',
    'notification.rules.delete': 'Bridge-side delete will not auto-restore. The app must explicitly save or enable the feature again.',
    'notification.statusReady': 'Waiting to read Notification Bridge status...',
    'notification.featureReady': 'Waiting for the app to register a notification feature...',
    'notification.actionReady': 'Waiting to call Notification Bridge APIs...',
    'notification.featureName': 'Starter Scheduled Reminder',
    'notification.featureMissing': 'Register this notification feature from the app first',
    'notification.registered': 'Notification feature registered or saved',
    'notification.toggled': 'App-side switch updated',
    'notification.directSent': 'Immediate notification sent',
    'notification.featureSent': 'Feature notification sent once',
    'notification.deleted': 'Notification feature deleted from the app side',
    'notification.directTitle': 'Starter Direct Notification',
    'notification.directContent': 'This is an immediate notification sent directly by the starter ceapp at runtime. Time: {time}',
    'notification.featureTitle': 'Starter Feature Notification',
    'notification.featureContent': 'This notification is sent through a registered feature. Time: {time}',
    'notification.missing': 'The current host does not expose Notification Bridge.',
    'ai.title': 'AI Bridge Example',
    'ai.body': 'A minimal AI Bridge usage sample. API keys stay in the host; the ceapp only declares capabilities and calls window.CanEngine.ai.',
    'ai.prompt': 'Introduce this ceapp template in one sentence.',
    'ai.text': 'Generate Text',
    'ai.status': 'Read Status',
    'ai.ready': 'Waiting for action...',
    'ai.missing': 'The current host does not expose AI Bridge.'
  }
}

const notificationRuleKeys = [
  'notification.rules.appOwned',
  'notification.rules.dualState',
  'notification.rules.delete'
]

const state = {
  notificationStatus: null,
  notificationFeatures: []
}

const i18n = window.CanEngineAppI18n.createI18n({
  appId: APP_ID,
  defaultLocale: 'zh-CN',
  messages
})

function t(key, vars) {
  return i18n.t(key, vars)
}

function getBridge() {
  return window.CanEngine || (window.parent && window.parent.CanEngine) || null
}

function setJSON(id, value) {
  const output = document.getElementById(id)
  if (!output) return
  output.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

function notificationAction(method, request, response) {
  setJSON('notification-action-output', {
    time: new Date().toISOString(),
    method,
    request,
    response
  })
}

function requireNotificationMethod(name) {
  const target = getBridge()?.notification
  const method = target?.[name]
  if (typeof method !== 'function') {
    throw new Error(t('notification.missing'))
  }
  return method.bind(target)
}

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

function setAIOutput(value) {
  setJSON('ai-output', value)
}

async function readAIStatus() {
  const bridge = getBridge()
  if (!bridge?.ai?.getStatus) {
    setAIOutput(t('ai.missing'))
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
    setAIOutput(t('ai.missing'))
    return
  }
  const prompt = document.getElementById('ai-prompt').value.trim() || t('ai.prompt')
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

function notificationFeatureRecord() {
  return state.notificationFeatures.find((item) => item?.featureId === DEMO_NOTIFICATION_FEATURE_ID) || null
}

function notificationFeatureConfig() {
  return {
    featureId: DEMO_NOTIFICATION_FEATURE_ID,
    name: t('notification.featureName'),
    triggerType: 'schedule',
    entry: 'starter.dailyBrief',
    schedule: {
      type: 'interval',
      everyMinutes: 60
    },
    level: 'info',
    defaultChannels: ['local'],
    sourceEnabled: true,
    reactivate: true
  }
}

function notificationStatusSummary(status, feature) {
  return {
    enabled: !!status?.enabled,
    permissionGranted: !!status?.permissionGranted,
    scheduleAllowed: !!status?.scheduleAllowed,
    defaultChannelId: status?.defaultChannelId || 'local',
    availableChannels: Array.isArray(status?.availableChannels) ? status.availableChannels : [],
    demoFeatureEffectiveStatus: feature?.effectiveStatus || 'not_registered',
    demoFeatureSourceEnabled: feature?.sourceEnabled ?? null,
    demoFeatureBridgeEnabled: feature?.bridgeEnabled ?? null
  }
}

function nowText() {
  return new Date().toLocaleString(i18n.getLocale())
}

async function refreshNotificationStatus() {
  try {
    const status = await requireNotificationMethod('getStatus')()
    const features = await requireNotificationMethod('listOwnFeatures')()
    state.notificationStatus = status || null
    state.notificationFeatures = Array.isArray(features) ? features : []
    const feature = notificationFeatureRecord()
    const statusReport = notificationStatusSummary(status, feature)
    setJSON('notification-status-output', statusReport)
    setJSON('notification-feature-output', feature ? {
      demoFeature: feature,
      allOwnFeatures: state.notificationFeatures
    } : {
      demoFeature: null,
      allOwnFeatures: state.notificationFeatures,
      note: t('notification.featureReady')
    })
    notificationAction('notification.getStatus + notification.listOwnFeatures', null, {
      status: statusReport,
      features: state.notificationFeatures
    })
  } catch (error) {
    const message = error?.message || String(error)
    setJSON('notification-status-output', message)
    setJSON('notification-feature-output', message)
    notificationAction('notification.getStatus + notification.listOwnFeatures', null, { error: message })
  }
}

async function registerNotificationFeature() {
  const request = notificationFeatureConfig()
  try {
    const response = await requireNotificationMethod('registerFeature')(request)
    await refreshNotificationStatus()
    notificationAction('notification.registerFeature', request, response)
  } catch (error) {
    notificationAction('notification.registerFeature', request, { error: error?.message || String(error) })
  }
}

async function toggleNotificationFeature() {
  const feature = notificationFeatureRecord()
  if (!feature) {
    notificationAction('notification.updateFeature', null, { error: t('notification.featureMissing') })
    return
  }
  const patch = {
    name: t('notification.featureName'),
    sourceEnabled: !feature.sourceEnabled
  }
  try {
    const response = await requireNotificationMethod('updateFeature')(DEMO_NOTIFICATION_FEATURE_ID, patch)
    await refreshNotificationStatus()
    notificationAction('notification.updateFeature', {
      featureId: DEMO_NOTIFICATION_FEATURE_ID,
      patch
    }, response)
  } catch (error) {
    notificationAction('notification.updateFeature', {
      featureId: DEMO_NOTIFICATION_FEATURE_ID,
      patch
    }, { error: error?.message || String(error) })
  }
}

async function sendDirectNotification() {
  const request = {
    title: t('notification.directTitle'),
    content: t('notification.directContent', { time: nowText() }),
    level: 'info',
    category: 'starter-direct'
  }
  try {
    const response = await requireNotificationMethod('send')(request)
    await refreshNotificationStatus()
    notificationAction('notification.send (direct)', request, response)
  } catch (error) {
    notificationAction('notification.send (direct)', request, { error: error?.message || String(error) })
  }
}

async function sendFeatureNotification() {
  const feature = notificationFeatureRecord()
  if (!feature) {
    notificationAction('notification.send (feature)', null, { error: t('notification.featureMissing') })
    return
  }
  const request = {
    featureId: DEMO_NOTIFICATION_FEATURE_ID,
    title: t('notification.featureTitle'),
    content: t('notification.featureContent', { time: nowText() }),
    level: 'info',
    category: 'starter-feature'
  }
  try {
    const response = await requireNotificationMethod('send')(request)
    await refreshNotificationStatus()
    notificationAction('notification.send (feature)', request, response)
  } catch (error) {
    notificationAction('notification.send (feature)', request, { error: error?.message || String(error) })
  }
}

async function deleteNotificationFeature() {
  try {
    await requireNotificationMethod('removeFeature')(DEMO_NOTIFICATION_FEATURE_ID)
    await refreshNotificationStatus()
    notificationAction('notification.removeFeature', {
      featureId: DEMO_NOTIFICATION_FEATURE_ID
    }, { success: true })
  } catch (error) {
    notificationAction('notification.removeFeature', {
      featureId: DEMO_NOTIFICATION_FEATURE_ID
    }, { error: error?.message || String(error) })
  }
}

async function openNotificationSettings() {
  try {
    await requireNotificationMethod('openSettings')()
    notificationAction('notification.openSettings', null, { opened: true })
  } catch (error) {
    notificationAction('notification.openSettings', null, { error: error?.message || String(error) })
  }
}

function render() {
  const locale = i18n.getLocale()

  document.title = t('app.title')
  document.documentElement.lang = locale
  document.getElementById('app-title').textContent = t('app.title')
  document.getElementById('app-subtitle').textContent = t('app.subtitle')
  document.getElementById('panel-title').textContent = t('panel.title')
  document.getElementById('panel-body').textContent = t('panel.body')
  document.getElementById('primary-action').textContent = t('panel.action')
  document.getElementById('notification-title').textContent = t('notification.title')
  document.getElementById('notification-body').textContent = t('notification.body')
  document.getElementById('notification-refresh').textContent = t('notification.refresh')
  document.getElementById('notification-open-settings').textContent = t('notification.openSettings')
  document.getElementById('notification-register').textContent = t('notification.register')
  document.getElementById('notification-toggle').textContent = t('notification.toggle')
  document.getElementById('notification-send-direct').textContent = t('notification.sendDirect')
  document.getElementById('notification-send-feature').textContent = t('notification.sendFeature')
  document.getElementById('notification-delete').textContent = t('notification.delete')
  document.getElementById('notification-rules-title').textContent = t('notification.rulesTitle')
  document.getElementById('notification-rules-list').innerHTML = notificationRuleKeys.map((key) => `<li>${t(key)}</li>`).join('')
  document.getElementById('ai-title').textContent = t('ai.title')
  document.getElementById('ai-body').textContent = t('ai.body')
  document.getElementById('ai-prompt').placeholder = t('ai.prompt')
  document.getElementById('ai-text-action').textContent = t('ai.text')
  document.getElementById('ai-status-action').textContent = t('ai.status')
}

function wireEvents() {
  document.getElementById('notification-refresh')?.addEventListener('click', refreshNotificationStatus)
  document.getElementById('notification-open-settings')?.addEventListener('click', openNotificationSettings)
  document.getElementById('notification-register')?.addEventListener('click', registerNotificationFeature)
  document.getElementById('notification-toggle')?.addEventListener('click', toggleNotificationFeature)
  document.getElementById('notification-send-direct')?.addEventListener('click', sendDirectNotification)
  document.getElementById('notification-send-feature')?.addEventListener('click', sendFeatureNotification)
  document.getElementById('notification-delete')?.addEventListener('click', deleteNotificationFeature)
  document.getElementById('ai-text-action')?.addEventListener('click', generateAIText)
  document.getElementById('ai-status-action')?.addEventListener('click', readAIStatus)
}

function init() {
  setJSON('notification-status-output', t('notification.statusReady'))
  setJSON('notification-feature-output', t('notification.featureReady'))
  setJSON('notification-action-output', t('notification.actionReady'))
  setAIOutput(t('ai.ready'))
  wireEvents()
  hydrateAssets()
  i18n.subscribe(render)
  refreshNotificationStatus()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true })
} else {
  init()
}
