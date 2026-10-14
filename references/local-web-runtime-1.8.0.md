# CEAPP Web Runtime — CanEngine 1.8.0

1.8.0 增加可选的 `runtime.web`。应用原有 HTTP 后端在打开应用时启动一次，关闭时回收；页面直接使用同一个后端，不再把每个 HTTP 查询改写成 `runJob`。旧版静态 HTML + Job 应用保持原有行为。

这适合数据库浏览器、知识库、文件管理器和已有 Python 网站。不是把任意网站完全自动转换：端口、可写目录、外部目录授权、离线依赖和后台守护进程仍需适配。

## 最小迁移

以现有 `ThreadingHTTPServer` 项目为例，在 CanEngine 仓库执行：

```sh
go run ./cmd/ceapp-web -src /path/to/website \
  -app-id my-library -name 'My Library' -version 1.8.0 \
  -server server.py -framework http-server \
  -data-read library:资料目录
```

生成器只新增 `app.json`，拒绝覆盖已有声明；不复制、不重写前端、路由或数据库模块。Host 版本是 1.8.0，应用自己的版本仍独立管理。默认识别唯一的 `server.py`、`app.py` 或 `main.py`；有多个入口时必须显式选择。

通常只需要以下几处配置调整：

1. `http-server` 适配器覆盖标准库 `HTTPServer` / `ThreadingHTTPServer` 的监听地址，原来的固定端口可以保留。自定义服务则读取 `CANENGINE_HOST` 和 `CANENGINE_PORT`。
2. 把数据库、上传、缓存、日志等可写文件放到 `CANENGINE_APP_DATA_DIR`；不要写回安装包，也不要硬编码用户 Home。
3. 外部资料、微信数据库或 Key 目录通过声明和原生选择器授权，读取 `CANENGINE_DATA_LIBRARY` 等变量。不再每次查询复制整个数据目录或 Key JSON。
4. 第三方 Python 依赖在打包阶段准备好，配置 `pythonPath`；静态 JS/CSS/字体也随包发布，首次启动无需 CDN 或在线安装。

例如：

```python
import os
from pathlib import Path

APP_DATA = Path(os.environ["CANENGINE_APP_DATA_DIR"])
LIBRARY = Path(os.environ["CANENGINE_DATA_LIBRARY"])
```

现有 `/api/...`、`fetch('/api/...')`、`<img src='/media/...'>`、表单、Range、HEAD、下载响应、SSE 和 WebSocket 使用原生 HTTP 语义，无需改成业务 Bridge RPC。原来的浏览器上传不需要新增原生目录授权，但后端仍必须把上传存入自己的可写目录。

Flask / FastAPI 生成器分别使用 `flask run --no-reload` 和 `uvicorn module:app`。可以用 `-args-json` 指定 factory、模块名或其他启动方式。必须关闭 debug/reload，不要自行打开系统浏览器，不要 daemonize、setsid 或派生脱离 Host 的后台服务。

```sh
go run ./cmd/ceapp-web -src /path/to/flask-project \
  -app-id flask-notes -framework flask -server app.py \
  -python-path vendor/python
```

使用所发布平台/架构兼容的 Python wheel，把依赖安装到项目的 `vendor/python`，再按原有方式签名打包。Host 使用 `python -S` 和干净环境：不会继承开发机的全局 site-packages、用户 PYTHONPATH 或 API Key。Python 的主脚本目录会正常加入搜索路径；`-m` 模式保留项目工作目录。二进制扩展和 SQLCipher 工具需要按目标平台随包或运行时提供。

## 声明示例

```json
{
  "schemaVersion": 1,
  "appId": "my-library",
  "name": "My Library",
  "nameI18n": { "zh-CN": "我的资料库", "en-US": "My Library" },
  "version": "1.8.0",
  "entry": "server.py",
  "minCanEngineVersion": "1.8.0",
  "platforms": [{ "os": "*", "arch": "*" }],
  "runtime": {
    "requirements": [{ "id": "base-runtime" }],
    "web": {
      "executable": "python3",
      "args": ["server.py"],
      "pythonAdapter": "http-server",
      "pythonPath": ["vendor/python"],
      "workingDir": ".",
      "entryPath": "/",
      "readyPath": "/health",
      "startupTimeoutMs": 20000,
      "network": "loopback",
      "dataDirectories": [
        { "id": "library", "label": "资料目录 / Library", "access": "read" }
      ]
    }
  },
  "commands": {},
  "permissions": ["web.files.read"]
}
```

`readyPath` 应返回 2xx/3xx，探测不跟随重定向。没有健康路由时可用 `/`；需要登录、首页返回 404 或大量初始化时应配置专用健康路由。超时最多 60 秒。`entry` 仍是包内存在的文件；对于 Web 应用不再把它读取为 srcDoc，可以填写后端入口。

`executable` 可以是运行时工具名称或包内相对路径，所以运行模型不限于 Python。参数是数组而非 shell 字符串；`${CANENGINE_PORT}` 等只展开 Host 定义的变量，不执行 shell，也不读取任意环境变量。保留 `commands` 可兼容应用原有批处理功能，但 Web 页面的受限 Bridge 不自动开放通用 `runJob`。

### 可选：选择一个 JSON 自动配置资料位置

需要从 Key/配置文件确定资料目录的应用，可添加 `runtime.web.setup`。设置 `deferred: true` 时，先以零外部资料权限打开应用界面；用户点击导入按钮后才进入原生选择器。应用必须能处理未配置状态，不能假定数据目录环境变量始终存在。没有该选项的旧应用保留启动时设置流程。

```json
"dataDirectories": [
  { "id": "wechat", "label": "微信聊天记录和附件", "labelI18n": { "en-US": "WeChat chats and attachments" }, "access": "read" },
  { "id": "image_config", "label": "图片解码资料", "labelI18n": { "en-US": "Image decoding data" }, "access": "read", "optional": true }
],
"setup": {
  "deferred": true,
  "fileLabel": "选择微信 Key JSON",
  "fileLabelI18n": { "en-US": "Choose your WeChat key JSON" },
  "format": "wcdb-key-bundle",
  "privatePath": "keys/selected.json",
  "directories": [
    { "id": "wechat", "jsonKey": "_db_dir", "parentLevels": 1, "requiredPaths": ["db_storage"] },
    { "id": "image_config", "fromDirectory": "wechat", "parentLevels": 2, "relativePath": "app_data" }
  ]
}
```

这是通用声明，不依赖 appId。`jsonKey` 是顶层绝对路径字符串；`fromDirectory` 引用之前已推导的目录。先取 0–4 级父目录，再附加包外资料的相对路径，检查目录存在和 `requiredPaths` 未逃逸。推导失败只对必需目录补问原生文件夹，可选目录缺失不弹出额外选择器。手动补选必需目录后会重新推导依赖目录。

JSON 最多 4 MiB，默认 `format: json-object`；`wcdb-key-bundle` 额外检查数据库相对路径和十六进制 `enc_key`。正常 macOS 微信账号布局的单文件只读导入，以原生文件选择作为用户的导入动作，不再追加后台运行说明/只读确认框。简化流程只适用于标准 `_db_dir → 账号/db_storage` 和可选同资料区 `app_data` 规则；非标准目录、任意 metadata 路径、写权限或 Internet 权限仍需明确原生授权。

选择被取消、JSON 无效或所属应用已关闭时，不保存、不授予目录、不启动新后端。成功导入通过受约束的 `os.Root` 原子写入应用私有目录，权限 0600。不授权 JSON 的整个父目录，不通过 Bridge 返回密钥。权限指纹、Home/Host/系统根目录限制、符号链接检查和读写声明仍生效。缺失/无效设置在延后导入模式下返回未配置界面；应用菜单“重新选择本地资料”撤销授权但保留私有数据。

延后启动目前只接受 loopback 与外部只读目录；未配置 profile 只存在于内存，不能序列化为授权。Windows 的本地网络隔离更宽，仍要求原生网络确认，不提供静默未授权启动。

页面导入示例（只在按钮点击后调用）：

```js
importButton.addEventListener('click', () => window.CanEngine.web.importData())
```

`importData()` 不接受路径、JSON 内容或授权目录参数。Host 绑定当前实例，显示原生选择器，完成验证后停止旧后端，以新权限启动并更新 iframe。页面只收到成功状态，不收到新的 Bridge token。关闭实例取消进行中的导入和启动；旧进程的延迟退出回调不会停止替换后的进程。CLI 可预览未配置界面，但不提供原生导入，也不会复用真实账号资料。

macOS Python 解析会避开 `/usr/bin/python3` 的 xcrun 代理，并在 Finder 的精简 PATH 下检查标准安装位置和直接解释器。它不会通过放宽整个 Xcode 或 Home 的沙箱权限来修复启动；Python 未安装时仍要求修复基础运行环境。

环境变量：

| 名称 | 用途 |
| --- | --- |
| `CANENGINE_HOST` / `CANENGINE_PORT` | 本地后端绑定地址和动态端口 |
| `CANENGINE_APP_DIR` | 只读安装包 |
| `CANENGINE_APP_DATA_DIR` | 该应用持久可写数据 |
| `CANENGINE_TEMP_DIR` | 实例私有临时目录，关闭后清理 |
| `CANENGINE_ORIGIN` | 前端固定 origin，配置 allowed-hosts / CSRF / 绝对 URL |
| `CANENGINE_DATA_<ID>` | 用户选择的外部目录，ID 大写 |

`HOME`、`USERPROFILE`、XDG 缓存和临时目录也重定向到该应用的私有目录。可选目录未被用户授权时，对应环境变量不存在。

## HTTP 与 Bridge 边界

每个应用使用独立的 `http://127.0.0.1:<固定端口>`，同时仅监听 `127.0.0.1` / `::1`。backend 端口每次启动变化，前端 origin 端口持久化，重开后 localStorage / IndexedDB 不因动态端口而丢失。固定端口被其他进程占用时明确报错，不悄悄更换 origin。

数字 loopback 不需要 DNS 或 hosts 配置。旧版 macOS WebKit 的 `.localhost` 子域解析并不可靠（[WebKit 160504](https://bugs.webkit.org/show_bug.cgi?id=160504)），因此没有采用该方案。发布包沿用现有 `NSAllowsLocalNetworking`，不关闭普通远程域名的 ATS；参见 [Apple ATS 配置](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSAppTransportSecurity)。

浏览器 Cookie 不按端口隔离，不能只给每个应用分配端口后就宣称完整隔离。Host 为每个 appId 保存独立 Cookie 容器：不会把任意浏览器 Cookie 转发给后端，也不会把后端 Set-Cookie 写入浏览器共享容器。注入脚本兼容普通 `document.cookie` getter/setter，按路径与 HttpOnly 筛选；每次 cookie 读写使用小型同源请求，而非 Job。普通 API 请求无需前端附加 Cookie RPC。session cookie 保留到 Host 退出，带期限的 cookie 原子保存于 Host 私有目录。每应用最多 256 项、每项 4 KiB、期限最多 400 天；未改变的持久 cookie 不重复写文件。

此容器面向本地 HTTP 网站的常见 cookie，不模拟 HTTPS Secure / `__Secure-` / `__Host-` / Partitioned cookie。全局 fetch 包装保留同源 `credentials: omit`；自行构建 fetch 实现、Worker 发出的显式 credentials: omit 和 Service Worker Cookie Store 等高级浏览器行为需单独验证，不是无条件零改造。Worker/原生 document.cookie 原型即使绕过 shim 写入共享浏览器容器，也不会进入后端请求或其他应用的 Host Cookie 容器。

Host 代理保留原来的请求路径、body、Content-Type 和 HTTP 流，移除不可信 forwarding 头，生成自己的 X-Forwarded 头；后端 Host 头仍是前端 origin。需要配置 allowed-hosts 的框架应接受 `CANENGINE_ORIGIN` 的 hostname。后端绝对 localhost 重定向会适配到应用 origin；Cookie Domain 在独立容器中归一为本应用。

HTML 最多缓冲 64 KiB 前缀以注入受限 Bridge，剩余内容流式传递。媒体和附件不转换为 base64，不进入 Job result 文件。HTML 禁用缓存，普通资源保留后端的缓存语义。后端必须支持 `Accept-Encoding: identity`；应用自己的 CSP 不会被删除，因此严格 CSP 必须允许同源 `/__canengine__/bridge.js`。保留路径 `/__canengine__/` 和参数 `__canengine_launch` 不可用于业务路由。iframe 页面需要允许被 Host 嵌入；原网站的 `X-Frame-Options: DENY/SAMEORIGIN` 或严格 `frame-ancestors` 需要有意识地调整。

页面收到的 `window.CanEngine` 仅包含语言、版本、能力查询、打开 HTTP(S) 外链，以及 `web.getStatus/onStatusChange/importData/saveAs/revealFile/download`。文件路径动作限定在该应用包、私有数据和已授权目录，且只能操作普通文件；另存为先用 `os.Root` 打开受约束的文件句柄，不在保存对话框之后重新打开不可信路径。跨 iframe 通信验证 source、origin、instanceId 和每次启动轮换的 token。页面不能通过该通道调用任意 Wails 方法、通用 Job、其他应用会话或任意宿主文件系统。

同源 `<a download>` 自动接到 `web.download`：Host 只请求当前实例的后端路由，携带该应用自己的 Cookie，流式写入 Host 私有临时文件，再显示原生另存为。不会访问任意外部 URL，也不能下载 Host 保留路由或重定向到其他服务。下载随应用关闭取消，超时最多 10 分钟。没有 `download` 属性的链接、Blob 下载、JS 自定义导出等需要原网站显式使用 `web.download(url, filename)` 或 `web.saveAs(path)`；不能假定所有 WebView 都有完整浏览器下载 UI。CLI 预览不模拟原生保存权限，正式导出在 CanEngine 中验证。

语言使用 `getLocale()` / `onLocaleChange()`，支持 `zh-CN` 和 `en-US`，原有网站如已有国际化只需接上这一处。示例 `Apps/web-host-demo` 提供本地双语资源，不依赖远程网页框架。

### 可选：转发会话到微信画布

需要将本地会话交给现有微信画布处理的 Web 应用，可声明精确权限 `canvas.wechat.import`，调用：

```js
const { canvasId, name } = await window.CanEngine.canvas.importWeChatArchive(
  '/api/conversations/exports/<opaque-task-id>/archive',
  'conversation.zip'
)
```

Host 只接受当前实例自己的 HTTP 下载地址，拒绝外部 URL、其他本地服务、Host 保留路由和跨源重定向。权限必须精确声明，通配符不会隐式授予此能力。内容解压总计最多 5 GiB，单文件同为 5 GiB，消息最多 100,000 条（追加后的画布也受约束），ZIP 条目最多 100,004；下载另预留 128 MiB 容器头部开销。原生导入并发上限为 1，下载超时 30 分钟，Bridge 等待最多 60 分钟；普通 web.download 仍为 10 分钟。导入检查磁盘余量，大文件分块复制，结构化消息与 TXT 流式解析并执行条数校验；应用关闭取消下载、复制和解压，失败清理私有下载及未完成的画布。页面只收到画布 ID 和名称，不会收到宿主路径、其他画布资料或通用 Canvas RPC 权限。

CanWeChat 的完整会话格式为 `canengine.wechat.conversation.v1`：ZIP 内包含 `canwechat-export.json`、`chat.json`（schema 3）、保留全部源字段的 `raw-messages.jsonl`、`missing-attachments.json` 和本地可用的 `attachments/`。`chat.json` 保留秒级时间、稳定 sourceId、结构化消息和附件引用；历史不完整时拒绝导入。未下载或暂不支持解码的附件单独列出，不冒充已包含。现有分享 ZIP/TXT 导入仍兼容。

导入成功后打开真正的微信画布，沿用其 Skill、AI 分析、身份和导出流程，不自动向外部 AI 发送资料。完成的画布独立保留；关闭来源应用只回收未完成任务和临时文件，不删除已导入画布。

CanWeChat 1.0.6 只保留顶部转发入口。浮层先准备私有清单，再选择消息类别和最大的 20 个附件。取消类别也取消其原始记录；只取消单个附件则保留对应消息。打包前显示预计大小和宽范围用时，完成后显示实际 ZIP 大小及耗时，再由用户确认交接。界面不常驻显示上限，仅超限错误中说明。按分库使用有界分页和同一 SQLCipher 只读事务，结束/取消即回收连接与子进程；并发 WAL 写入不再使扫描失效。清单固定本次读取的记录，打包不重新读取数据库，但保留附件签名、账号/密钥代次及最新时间校验。失败可“重新整理”：取消旧任务、刷新统计并重建清单，保留有效选择；原生导入失败可复用已准备 ZIP 重试。估时不保证磁盘速度或成功；历史不完整、附件改变、超限或空间不足都明确报错，不静默截断。微信画布保留主动取消与缺失附件说明；消息列表先渲染最近 500 条、按需加载更早内容。

### 画布分段文本读取

CanEngine MCP 发布 `read_canvas_text_range({canvasId, path, offset:0, maxBytes:65536})`，`read_canvas_file` 也接受相同分页字段，兼容缓存工具清单的客户端。返回 `content`、`offset`、`nextOffset`、`totalBytes`、`revision`、`eof`、`partial`；后续请求复用返回的 `canvasId`、`revision` 及 `nextOffset`，直到 `eof=true`。每页默认 64 KiB、上限 256 KiB，整份文本可超过原整文件响应限制；不先读完整文件进内存。偏移按 UTF-8 字节计，保证字符不被截断，但行/JSON 记录可能跨页。文件替换或修改返回 `FILE_CHANGED`，从零重读，避免跨版本拼接。路径、Full Access、符号链接和 Skill 隔离检查沿用画布现有规则；该工具只向画布 MCP 发布，不向 CEAPP Bridge 扩权。画布工作上下文与微信 AI 指令同步说明读取方法，并要求未完成全量读取时如实说明实际分析范围。已有大 `chat.json` 无需重新转发。

## 实例级读取缓存（1.8.0）

Host 为每个常驻应用提供私有、仅内存的 JSON 响应缓存。迁移时通常只需让可短期复用的读取接口返回标准 `Cache-Control: private, max-age=5`（例如会话、联系人分页）。无需重写 `fetch` 成 Bridge RPC；但原网站显式使用 `fetch(..., {cache: 'no-store'})` 时仍会绕过缓存，请仅对可缓存读取移除该选项。Host 尊重请求/响应的 `no-store`、响应的 `no-cache` 和刷新请求，不猜测业务数据是否可以缓存。

每实例最多 32 MiB、256 项，单响应正文最多 2 MiB，TTL 上限 60 秒，LRU 淘汰；相同在途请求合并。缓存身份包括完整 URL/查询参数、Cookie、Authorization、credentials: omit 和其他端到端请求头，支持 Vary 维度，不跨应用、账号或进程重开共享。缓存填充最多等待 60 秒，单个等待者取消不影响其他请求。关闭/权限撤销/后端退出时清理正文并取消读取，没有把聊天资料或响应持久化到 Host 文件夹。

所有非 GET/HEAD/OPTIONS 请求在开始和响应到达时均失效缓存；Cookie 更新也失效。代际检查阻止写操作之前的并发读取回填旧内容。应用主动刷新可用原来的 POST 刷新接口，或 GET `Cache-Control: no-cache` / `fetch(..., {cache: 'reload'})`；如数据还缓存在后端内存，POST 刷新接口也应清理后端业务缓存。外部进程改动资料时最多存在声明 TTL 的延迟，Host 不会擅自监听用户磁盘或理解数据库结构。

只有成功且明确声明新鲜期的 JSON 可缓存。HTML、Set-Cookie、Vary: *、条件请求、Range、HEAD、下载、压缩响应、SSE、WebSocket、视频和其他二进制继续走原有 HTTP 流。受缓存管理的 JSON 对浏览器发送 `no-store`，使新鲜期和换账号失效统一由 Host 控制，避免第二层浏览器缓存绕过账号切换；普通媒体仍保留原资源缓存头。Origin/Host 校验先于缓存命中执行，文件沙箱、签名、目录权限和受限 Bridge 均不改变。

`CanEngine.web.getStatus().cache` 提供 hits、misses、coalesced、entries、bytes、evictions 数字；响应 `X-CanEngine-Cache` 为 HIT/MISS/COALESCED/BYPASS。诊断不返回 URL、查询参数、密钥或正文。此能力减少重复后端查询，并不自动虚拟化第三方网站的 DOM，也不把 SQLCipher CLI 自动替换为持久连接。

## 安全与生命周期

签名、安装来源、License 和平台检查沿用原有 CEAPP 流程，不引入未签名的生产安装入口。首次运行需要原生确认；普通应用逐项选择目录，JSON 设置应用统一确认 Host 推导出的具体目录。只读与可写权限分开声明。授权绑定完整 manifest 指纹，版本/配置改变会重新确认；禁止授权 Host 内部目录、Home 根目录和宽泛系统根目录，也拒绝路径逃逸和重叠授权。应用菜单可以重新选择本地资料，停止后端但保留数据。

| 平台 | 后端隔离实现 | 注意事项 |
| --- | --- | --- |
| macOS | sandbox-exec；包、解释器、系统工具只读，数据/临时/已授权目录按权限访问 | 默认只能绑定自身 loopback 端口，不能连接其他本机服务；需要系统仍支持该隔离器 |
| Linux | bubblewrap + PID namespace；默认独立网络 namespace，通过私有 Unix socket relay 连到 Host | 必须安装 bwrap 并允许 user namespace；联网模式共享宿主网络，需显式确认 |
| Windows | 已校验的 wxc-exec ProcessContainer + 文件隔离 + kill-on-close Job Object | 必须有可用的安全执行器；私有网络能力用于 loopback，也可能包含局域网访问，不应声称是严格的“仅自身端口”隔离 |

任一平台的必要沙箱不可用就停止启动，不降级为普通 python3。仅测试注入的 launcher 绕过此要求，生产和 CLI 预览都使用真实沙箱。系统/解释器工具目录是受控只读环境，不代表对整个宿主文件系统完全无可见性。

默认页面增加同源资源/连接 CSP；联网需 `network: internet` 和 `web.network`。CSP 是页面资源策略，不是通用 OS 网络防火墙，也不能阻止任意页面自身导航。HTTP Origin/Host/Referer/启动 token 检查用于浏览器 CSRF 与 DNS rebinding 防护，**不构成对同一 OS 用户下任意本地程序的密码学鉴权**：本地程序能够伪造 HTTP 头。尤其在 Windows 私有网络能力下，不能把它描述成对恶意其他应用的完全 HTTP 隔离。需要不信任原生同用户程序的部署，应另行引入平台 WebView 协议代理/持有句柄的 IPC，而不能仅加强前端缓存或宣传 token 可以解决这一边界。

Host 对一个 appId 只启动一个实例。关闭应用标签、卸载、覆盖安装、注销账号或退出 Host 会停止代理、HTTP/WS 连接和进程树，清理实例临时文件，保留 app_data。主窗口的关闭按钮仍沿用 CanEngine 的托盘/后台行为，隐藏主窗口不等于退出 Host；切换到另一应用也不结束已打开标签的后端。启动中关闭会取消启动；后端崩溃停止代理并显示错误，不在后台无限自动重启。Unix 用进程组和父进程死亡管道；Windows 用 kill-on-close Job Object。常规子进程继承边界；恶意/主动 daemonize 脱离 Unix 进程组不受支持。应用启动按原流程检查 License，运行中每分钟检查授权，不在每次查询重复检查。

资源控制包括 64 KiB 后端日志尾部、128 个并发 HTTP 流、有限头部与就绪超时、Bridge 并发与超时、关闭时 TERM→KILL。没有实现跨平台硬性 CPU/内存/磁盘配额；后端连接池、线程数、大查询取消和数据库写入策略仍由应用管理。数据库不要共享一个非线程安全连接给所有线程：按库要求使用锁或连接池。

## 性能与 CanWeChat

以下开销从每次查询移到一次应用启动：进程启动、Python import、Key 初始化、状态缓存建立、manifest/运行配置与权限准备。Web HTTP 请求不创建 Job、不 materialize staged input、不复制 Key JSON、不生成 stdout JSON、response/result/metadata 文件，也不等待整个后端退出才返回。

此功能不会自动把 `query_db()` 里的 `subprocess.run(sqlcipher ...)` 变成持久数据库连接。CanWeChat 回到常驻服务后可以复用 `key_manager`、`table_to_db`、Name2Id、联系人及头像缓存，但 SQLCipher CLI 启动/解密开销仍然存在；下一步应由该应用采用兼容的 SQLCipher Python binding 和受控连接池。对数据库的解密设置、线程安全、外部 SQLite/WAL 文件权限必须按实际数据库要求验证，不能简单换成普通 sqlite3。

旧 Job Runner 同时修复了超长 stdout 单行停止排水导致子进程卡住的问题：日志持续排水，内存捕获每流最多 8 MiB，完整内容仍写 Job 日志；超过限制时需要 result.json / 文件结果，不依赖无限 stdout。这是独立兼容性修复，并不是常驻后端的替代方案。

## 验证、预览与打包

```sh
go test -race ./internal/engine -run 'TestWeb|TestRunnerDrains|TestRunnerCaps'
go test ./cmd/ceapp-web
go run ./cmd/ceapp-web -src Apps/web-host-demo -preview
```

CLI 预览不会安装应用，使用临时数据并在 Ctrl+C 后清理。声明外部数据目录的应用必须在 CanEngine 原生授权后预览，CLI 不自动授权真实资料。`-native-preview` 是额外开发调试入口，需要 Wails production 编译标签及平台链接参数；macOS 可使用：

```sh
go run -tags production ./cmd/ceapp-web -src Apps/web-host-demo -native-preview
```

常规发布继续使用 CanEngine 内置签名器，或 `go run ./cmd/ceapp-pack -src ... -out ... -private-key-file ... -key-id ...`。测试使用临时 Ed25519 密钥校验 demo 的打包、签名、验签和解包，不接触发布者私钥。

回归用例覆盖重复请求保留 PID/SQLite connectionId、关闭重开保存笔记且保持 origin、无 Job 目录、HTTP upload/download/HEAD/Range、即时 SSE、WS upgrade、CSRF、应用 Cookie 隔离、启动取消、并发关闭、授权撤销、子进程回收和真实 macOS 目录沙箱。macOS 15.6.1 原生 Wails 窗口已实际加载 demo，连续点击读取时 PID 与 connectionId 不变。demo 的 20 次查询毫秒级结果只是小型 SQLite 协议测试，不是 CanWeChat 大库性能实测；Windows/Linux 已通过交叉编译，仍需在目标机器验证执行器/namespace 和 WebView。
