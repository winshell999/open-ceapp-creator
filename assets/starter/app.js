// Rename APP_ID together with app.json before building your app.
const APP_ID = 'starter-app'
const NOTE_COLLECTION = 'starter_notes'
const BROWSER_STORAGE_KEY = `${APP_ID}.browser-notes`

const messages = {
  'zh-CN': {
    'app.eyebrow': 'Offline-first CEAPP starter',
    'app.title': 'Starter Notes',
    'app.subtitle': '一个小而完整的起点：离线界面、双语、真实本地功能、浏览器回退和最小权限。',
    'status.host': 'CanEngine 已连接',
    'status.browser': '浏览器预览模式',
    'status.bridgeStorage': 'Data Bridge',
    'status.browserStorage': '浏览器本地回退',
    'intro.title': '先完成一个有用的核心',
    'intro.body': '不要从框架或全部桥接能力开始。先让一个真实任务在没有网络时也能完成。',
    'intro.ruleUseful': '核心功能在首屏可理解、可操作、可验证。',
    'intro.ruleLocal': 'HTML、CSS、JS、图标和语言表都在项目内。',
    'intro.ruleMinimal': '每个权限都有对应的用户动作和降级状态。',
    'notes.title': '本地记录',
    'notes.body': 'CanEngine 中使用 app-private Data Bridge；普通浏览器中使用隔离的 localStorage，方便调试。',
    'notes.label': '记录内容',
    'notes.placeholder': '例如：替换应用名称和图标',
    'notes.add': '添加记录',
    'notes.empty': '还没有记录。添加一条来验证持久化。',
    'notes.delete': '删除',
    'notes.saved': '记录已保存。',
    'notes.removed': '记录已删除。',
    'files.title': '标准文件输入',
    'files.body': '选择、拖入或粘贴文件，并统一成浏览器 File。图片预览使用 object URL，不复制成 base64。',
    'files.pick': '选择文件',
    'files.dropTitle': '拖入文件或粘贴图片',
    'files.dropBody': '如果产品需要宿主任务，再按需添加 stageFile。',
    'files.empty': '尚未选择文件。',
    'release.title': '发布前再加能力',
    'release.body': '保留这个核心结构，按产品需要从 references 中加入 AI、Phone Bridge、通知、任务或共享数据。',
    'release.offline': '离线首屏',
    'release.offlineBody': '没有远程 CSS、JS、字体或图标。',
    'release.locale': '当前语言',
    'release.permission': '已声明权限',
    'error.data': '本地数据操作失败：{message}'
  },
  'en-US': {
    'app.eyebrow': 'Offline-first CEAPP starter',
    'app.title': 'Starter Notes',
    'app.subtitle': 'A small but complete starting point: offline UI, two locales, a useful local feature, browser fallback, and minimal permissions.',
    'status.host': 'CanEngine connected',
    'status.browser': 'Browser preview mode',
    'status.bridgeStorage': 'Data Bridge',
    'status.browserStorage': 'Browser local fallback',
    'intro.title': 'Finish one useful core first',
    'intro.body': 'Do not begin with a framework or every bridge. Make one real task understandable and usable without a network connection.',
    'intro.ruleUseful': 'The core feature is understandable, actionable, and testable on the first screen.',
    'intro.ruleLocal': 'HTML, CSS, JS, icons, and locale tables stay inside the project.',
    'intro.ruleMinimal': 'Every permission has a user action and an unavailable state.',
    'notes.title': 'Local notes',
    'notes.body': 'Use app-private Data Bridge in CanEngine and isolated localStorage in a normal browser for easy debugging.',
    'notes.label': 'Note content',
    'notes.placeholder': 'For example: replace the app name and icon',
    'notes.add': 'Add note',
    'notes.empty': 'No notes yet. Add one to verify persistence.',
    'notes.delete': 'Delete',
    'notes.saved': 'Note saved.',
    'notes.removed': 'Note deleted.',
    'files.title': 'Standard file input',
    'files.body': 'Pick, drop, or paste a file and normalize it to a browser File. Image preview uses an object URL instead of a base64 copy.',
    'files.pick': 'Choose file',
    'files.dropTitle': 'Drop a file or paste an image',
    'files.dropBody': 'Add stageFile later only if the product needs a host job.',
    'files.empty': 'No file selected yet.',
    'release.title': 'Add capabilities before release',
    'release.body': 'Keep this core structure and add AI, Phone Bridge, notifications, jobs, or shared data from the references only when the product needs them.',
    'release.offline': 'Offline first screen',
    'release.offlineBody': 'No remote CSS, JS, font, or icon dependency.',
    'release.locale': 'Current locale',
    'release.permission': 'Declared permissions',
    'error.data': 'Local data operation failed: {message}'
  }
}

const state = {
  notes: [],
  storageMode: 'browser',
  file: null,
  previewURL: ''
}

const i18n = window.CanEngineAppI18n.createI18n({
  appId: APP_ID,
  defaultLocale: 'zh-CN',
  messages
})

const $ = (id) => document.getElementById(id)

function t(key, vars) {
  return i18n.t(key, vars)
}

function getBridge() {
  return window.CanEngine || (window.parent && window.parent.CanEngine) || null
}

function escapeHTML(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]))
}

function toast(message, type = '') {
  const element = $('toast')
  element.textContent = message
  element.className = `toast ${type}`.trim()
  element.hidden = false
  clearTimeout(toast.timer)
  toast.timer = window.setTimeout(() => { element.hidden = true }, 2800)
}

function renderLocale() {
  document.title = t('app.title')
  document.documentElement.lang = i18n.getLocale()
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    element.textContent = t(element.dataset.i18n)
  })
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder)
  })
  $('host-status').textContent = t(getBridge() ? 'status.host' : 'status.browser')
  $('storage-mode').textContent = t(state.storageMode === 'bridge' ? 'status.bridgeStorage' : 'status.browserStorage')
  $('locale-value').textContent = i18n.getLocale()
  renderNotes()
  renderFile()
}

async function hydrateLogo() {
  const bridge = getBridge()
  if (!bridge?.assetURL) return
  try {
    $('app-logo').src = await bridge.assetURL(APP_ID, 'assets/logo.png')
  } catch {
    // Keep the relative URL for standalone browser debugging.
  }
}

function browserNotes() {
  try {
    const value = JSON.parse(localStorage.getItem(BROWSER_STORAGE_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch {
    return []
  }
}

function saveBrowserNotes(notes) {
  localStorage.setItem(BROWSER_STORAGE_KEY, JSON.stringify(notes))
}

function bridgeStore() {
  const bridge = getBridge()
  return bridge?.data?.local ? bridge.data.local(NOTE_COLLECTION) : null
}

async function loadNotes() {
  try {
    const store = bridgeStore()
    if (store?.find) {
      const result = await store.find({ limit: 100 })
      state.notes = Array.isArray(result) ? result : (result?.rows || [])
      state.storageMode = 'bridge'
    } else {
      state.notes = browserNotes()
      state.storageMode = 'browser'
    }
    state.notes.sort((left, right) => String(right.createdAt || '').localeCompare(String(left.createdAt || '')))
  } catch (error) {
    state.notes = browserNotes()
    state.storageMode = 'browser'
    toast(t('error.data', { message: error?.message || String(error) }), 'error')
  }
  renderLocale()
}

async function addNote(title) {
  const note = {
    id: `note-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    title,
    createdAt: new Date().toISOString()
  }
  const store = bridgeStore()
  if (store?.put) {
    await store.put(note)
  } else {
    saveBrowserNotes([note, ...browserNotes()])
  }
  await loadNotes()
  toast(t('notes.saved'))
}

async function deleteNote(id) {
  try {
    const store = bridgeStore()
    if (store?.delete) {
      await store.delete(id)
    } else {
      saveBrowserNotes(browserNotes().filter((note) => note.id !== id))
    }
    await loadNotes()
    toast(t('notes.removed'))
  } catch (error) {
    toast(t('error.data', { message: error?.message || String(error) }), 'error')
  }
}

function renderNotes() {
  const list = $('notes-list')
  if (!list) return
  if (!state.notes.length) {
    list.innerHTML = `<div class="empty-state">${escapeHTML(t('notes.empty'))}</div>`
    return
  }
  list.innerHTML = state.notes.map((note) => `
    <article class="note-row">
      <div><strong>${escapeHTML(note.title || '')}</strong><small>${escapeHTML(new Date(note.createdAt || Date.now()).toLocaleString(i18n.getLocale()))}</small></div>
      <button class="button secondary" type="button" data-delete-note="${escapeHTML(note.id)}">${escapeHTML(t('notes.delete'))}</button>
    </article>
  `).join('')
  document.querySelectorAll('[data-delete-note]').forEach((button) => {
    button.addEventListener('click', () => deleteNote(button.dataset.deleteNote))
  })
}

function isImage(file) {
  return String(file?.type || '').startsWith('image/') || /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(file?.name || '')
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function acceptFile(file) {
  if (!file) return
  if (state.previewURL) URL.revokeObjectURL(state.previewURL)
  state.file = file
  state.previewURL = isImage(file) ? URL.createObjectURL(file) : ''
  renderFile()
}

function renderFile() {
  const target = $('file-preview')
  if (!target) return
  if (!state.file) {
    target.className = 'file-preview empty'
    target.textContent = t('files.empty')
    return
  }
  const extension = (state.file.name.split('.').pop() || 'FILE').slice(0, 6).toUpperCase()
  const visual = state.previewURL
    ? `<img src="${escapeHTML(state.previewURL)}" alt="${escapeHTML(state.file.name)}">`
    : `<div class="file-icon">${escapeHTML(extension)}</div>`
  target.className = 'file-preview'
  target.innerHTML = `${visual}<div class="file-meta"><strong>${escapeHTML(state.file.name)}</strong><span>${escapeHTML(state.file.type || 'application/octet-stream')}</span><span>${escapeHTML(formatSize(state.file.size))}</span></div>`
}

function installEvents() {
  $('note-form').addEventListener('submit', async (event) => {
    event.preventDefault()
    const input = $('note-input')
    const title = input.value.trim()
    if (!title) return
    try {
      await addNote(title)
      input.value = ''
    } catch (error) {
      toast(t('error.data', { message: error?.message || String(error) }), 'error')
    }
  })

  $('pick-file').addEventListener('click', () => $('file-input').click())
  $('file-input').addEventListener('change', (event) => acceptFile(event.target.files?.[0]))

  const dropZone = $('drop-zone')
  dropZone.addEventListener('dragover', (event) => {
    event.preventDefault()
    dropZone.classList.add('dragging')
  })
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'))
  dropZone.addEventListener('drop', (event) => {
    event.preventDefault()
    dropZone.classList.remove('dragging')
    acceptFile(event.dataTransfer?.files?.[0])
  })

  document.addEventListener('paste', (event) => {
    if (['INPUT', 'TEXTAREA'].includes(event.target?.tagName)) return
    const file = Array.from(event.clipboardData?.items || [])
      .filter((item) => item.kind === 'file')
      .map((item) => item.getAsFile())
      .find(Boolean)
    if (file) {
      event.preventDefault()
      acceptFile(file)
    }
  })
}

async function init() {
  installEvents()
  i18n.subscribe(renderLocale)
  await Promise.all([hydrateLogo(), loadNotes()])
}

window.addEventListener('beforeunload', () => {
  if (state.previewURL) URL.revokeObjectURL(state.previewURL)
  i18n.dispose()
})

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init, { once: true })
} else {
  init()
}
