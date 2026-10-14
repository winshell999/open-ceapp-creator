const i18n = CanEngineAppI18n.createI18n({ appId: 'web-host-demo', messages: {
  'zh-CN': {
    title: '保留原网站，复用后端状态', description: '每次刷新都请求原来的 /api/status。进程和数据库连接保持不变；关闭并重开后，笔记仍会保留。',
    pid: '后端进程', connection: '数据库连接', requests: '累计请求', refresh: '再次读取', notes: '持久化笔记', save: '保存', files: '原生 HTTP 上传与下载', download: '下载示例文件', uploaded: '已上传 {size} 字节'
  },
  'en-US': {
    title: 'Keep the website, reuse backend state', description: 'Each refresh calls the original /api/status. The process and database connection stay the same. Notes survive closing and reopening the app.',
    pid: 'Backend process', connection: 'Database connection', requests: 'Requests served', refresh: 'Read again', notes: 'Persistent notes', save: 'Save', files: 'Standard HTTP upload & download', download: 'Download sample file', uploaded: 'Uploaded {size} bytes'
  }
} })

i18n.subscribe(() => {
  document.title = i18n.t('title')
  document.querySelectorAll('[data-i18n]').forEach((element) => { element.textContent = i18n.t(element.dataset.i18n) })
})

async function refresh() {
  const response = await fetch('/api/status')
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  const status = await response.json()
  document.querySelector('#pid').textContent = status.pid
  document.querySelector('#connection').textContent = status.connectionId
  document.querySelector('#requests').textContent = status.requests
  const list = document.querySelector('#notes')
  list.replaceChildren(...status.notes.map((note) => { const item = document.createElement('li'); item.textContent = note.text; return item }))
  localStorage.setItem('lastPid', String(status.pid))
}
function report(error) { document.querySelector('#result').textContent = error.message }
document.querySelector('#refresh').onclick = () => refresh().catch(report)
document.querySelector('#note-form').onsubmit = async (event) => {
  event.preventDefault()
  try {
    const input = document.querySelector('#note')
    const response = await fetch('/api/notes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: input.value }) })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    input.value = ''
    await refresh()
  } catch (error) { report(error) }
}
document.querySelector('#upload').onchange = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const response = await fetch('/api/upload', { method: 'POST', body: file })
    const result = await response.json()
    document.querySelector('#result').textContent = i18n.t('uploaded', { size: result.size })
  } catch (error) { report(error) }
}
refresh().catch(report)
