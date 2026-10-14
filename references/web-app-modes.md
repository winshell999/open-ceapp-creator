# CEAPP创建模式

先判断业务意图。网站地址加“一键填写/快速预填”选择1.8.0的form-prefill，按[网站预填流程](form-prefill.md)调研字段并生成受控JSON调用；不能选择没有Host Bridge的remote-web或用iframe跨域操作。仅要求联网封装已有公网网站时选择remote-web；不要要求复制网站源码或制作HTML占位页。常驻本地HTTP后端使用1.8.0+的runtime.web；完整Host Bridge和离散任务使用本地HTML模式。

## 网站表单预填 · 1.8.0

本地runtime.web业务界面使用`CanEngine.browser.prefill(request)`打开固定授权官网并在右侧原生浏览器填入字段。manifest同时声明`browser.form.prefill`、`form-prefill-v1`和1–16个HTTPS targets。运行时只提交目标ID和字段JSON，不提交URL/JS。需使用包含此桥接实现的1.8.0+宿主；已有数据库和业务调用保持，验证码、同意及最终提交始终人工。

```bash
python scripts/create_ceapp.py --profile form-prefill --app-id my-prefill \
  --name "表单预填" --url 'https://actual.example/form' \
  --mapping /path/to/researched-request.json --output /path/to/new-app
```

示例URL需替换为真实目标；mapping由Agent调研实际DOM后生成，仅使用虚构测试值，生产默认值清空。完整契约、字段格式、事件/依赖、隐私和CanEngine实机验收见[form-prefill.md](form-prefill.md)。标准顶层原生控件可复用通用接口，跨域iframe、Shadow DOM和自定义组件须手工或独立受审适配，不能承诺所有网站都直接适用。

## 远程网站 · 1.8.0

```bash
python scripts/create_ceapp.py --profile remote-web --app-id my-website \
  --name "远程网站" --url https://example.com/app/ \
  --storage persistent --output /path/to/new-app
python scripts/validate_ceapp.py /path/to/new-app
```

可重复传 `--allowed-origin https://login.example.com`。源目录只有app.json、包内图标和说明。正式签名打包流程保持不变。最低宿主1.8.0，应用版本独立；macOS 14+或Windows amd64/WebView2。Linux尚未支持，Windows实现需要目标机器原生验收。

```json
{
  "schemaVersion": 1,
  "appId": "my-website",
  "name": "My Website",
  "nameI18n": { "zh-CN": "我的网站", "en-US": "My Website" },
  "version": "1.8.0",
  "minCanEngineVersion": "1.8.0",
  "platforms": [{ "os": "darwin", "arch": "*" }, { "os": "windows", "arch": "amd64" }],
  "runtime": { "remoteWeb": { "url": "https://example.com/app/", "storage": "persistent" } },
  "permissions": ["web.network"]
}
```

entry可省略，Host在容器内部使用app.json作为文件锚点；不要填远程URL作为entry。禁止混入runtime.web、commands、environment、runtime requirements、fileDialog和capabilities。不要添加占位echo/Python，不要附带网站后端或秘钥，不注入CanEngine/Wails接口。

只接受没有内嵌凭据的HTTPS URL；开发允许数字loopback HTTP。入口origin自动允许。allowedOrigins是精确主页面导航origin，不接受通配符、路径或参数；需要跨域登录时仅增加真实必要域名。它不充当资源请求防火墙，网站CORS/CSP照常生效。TLS使用系统校验。

Host在主窗口右侧嵌入独立原生网站视图，保留左侧导航。网站仍作为自己的主文档加载，避开iframe第三方存储条件。默认persistent按Host资料目录/appId保存独立Cookie、localStorage、IndexedDB和资源缓存；不与系统浏览器或别的appId共享。更新保持appId可复用存储。切换应用只隐藏网页，返回保留当前页面。ephemeral在应用关闭后丢弃，刷新和切换期间仍可用。测试/生产用不同appId。

资源缓存遵守网站HTTP头和浏览器策略，不能承诺离线启动、session cookie跨进程保存、任意Service Worker行为或业务分析结果持久化。清理资源缓存保留Cookie/DOM；清除网站数据有原生确认，会退出网站账号并删除本地网站数据。浏览器打开使用系统浏览器的登录状态。

网页随右侧区域缩放，不另开窗口，不添加返回/前进/刷新/首页导航栏，也不预留其高度。宿主对话框、菜单和通知遮罩出现时暂时隐藏网页，关闭后恢复。刷新、浏览器打开、清理资源缓存、清除网站数据在左侧正在运行的应用右键菜单中；错误时右侧提供重试。此布局为远程模式默认行为，无需新的manifest字段或文件包。

CanEngine入口与原生确认框有zh-CN/en-US；网站语言由网站自己决定。文件输入/下载由原生WebView负责。新窗口链接目前在当前网站视图导航；OAuth弹窗/opener、特殊下载、摄像头等需网站专门验收。静态Host Bridge、AI、Data、Phone和Python任务不在远程页面暴露。不能用Connector或Wails私有API弥补这一边界。

宿主与应用版本独立，已有版本号只有用户明确要求时才变更。本次远程能力加入当前1.8.0源码，需使用包含此实现的1.8.0构建；不能靠降低app.json最低版本让旧二进制获得新功能。

通用示例见assets/remote-web，只含占位地址和公开配置。联网封装不会自动增加网站尚未实现的持久化或授权能力。

### 受保护远程网站

需要限制在CanEngine中使用时，生成`remote-web --authorization canengine`，写入`runtime.remoteWeb.authorization: "canengine"`，最低宿主为包含此功能的1.8.0构建。网站登记与服务端票据校验是必要条件；网站密钥、License Token和PHP代码不放进CEAPP目录。单文件PHP首页、固定入口和隐私规则见[remote-web-authorization.md](remote-web-authorization.md)。

## 本地常驻网站 · 1.8.0

生成可运行协议示例：

```bash
python scripts/create_ceapp.py --profile web-python --app-id my-local-web --name "My Local Web" --output /path/to/new-app
```

迁移已有网站使用Host的 `go run ./cmd/ceapp-web -src ...`，参见完整的[1.8.0规则](local-web-runtime-1.8.0.md)。只新增声明，保留既有前端、路由、数据库和HTTP语义。摘要：

- runtime.web启动一次常驻后端，HTTP查询不逐次创建Job；entry仍为包内真实文件，commands允许为空。
- pythonAdapter:http-server或显式CANENGINE_HOST/PORT；Flask/FastAPI关闭reload/daemonize/自动打开浏览器。可使用其他受支持运行时或包内可执行程序。
- CANENGINE_APP_DATA_DIR持久可写、TEMP_DIR实例临时、APP_DIR包只读。Home/XDG也私有化；不能写回包或硬编码开发机路径。
- 外部目录通过dataDirectories/read或read-write授权，权限web.files.read/web.files.write；network:internet需web.network。第三方Python/JS/字体在打包阶段本地准备，不继承开发机site-packages/API Key。
- setup支持声明式JSON目录推导、可选目录及deferred导入。web.importData无路径参数，Host验证并原子保存0600私有设置；不把Key或整个父目录传回页面。deferred仅loopback与只读目录，Windows仍需原生网络确认。
- appId有持久固定loopback origin；重开localStorage/IndexedDB不因后端端口变化丢失。Host独立Cookie容器隔离后端账号，持久Cookie与session cookie寿命不同；不模拟完整HTTPS/Partitioned Cookie行为。
- HTTP保留表单、文件上传、HEAD/Range、媒体流、SSE和WS；下载用受限web.download/saveAs/revealFile。CLI预览不证明原生另存为。
- 1.8.0 Web Bridge提供语言/版本/能力/外链及web状态、导入、文件动作；匹配1.8.0+构建另外提供有明确声明/权限的browser预填。通用runJob/AI/Data/Phone不可假设可用。CSP与frame-ancestors必须允许本地应用被Host加载，不能删除网站安全头来掩盖问题；原生预填目标不通过跨域iframe加载。
- 明确新鲜期的JSON读取可缓存：每实例32MiB/256项、单响应2MiB、TTL至多60秒、LRU/在途合并；Cookie/Authorization和请求头参与隔离；写操作、Cookie更新、关闭与授权撤销失效。HTML、SSE、WS、附件、no-store等旁路。cache诊断只给数字，不暴露URL/正文。不会自动持久化响应或虚拟化DOM。
- 可精确声明canvas.wechat.import，将当前后端自己的会话ZIP交给微信画布；受内容数量/大小/磁盘/并发/取消限制。Canvas文本分页工具属于作者MCP，不因此扩张CEAPP Bridge。
- macOS/Linux/Windows使用各自沙箱，必要隔离器缺失时停止；关闭标签、卸载、覆盖、注销、退出回收进程/连接，保留app_data。切换标签、隐藏主窗口不等于退出。无跨平台硬CPU/内存配额，数据库连接池仍由应用实现。

完整1.8.0文档保留更精确的限制及已验收/待验收状态，不把协议示例性能当真实大库性能。

## 本地HTML与任务

沿用原来的九个能力profile、公开Bridge Adapter与Job规则。远程网站例外不会放宽本地工具的权限、离线首屏或脚本声明要求。不要让所有业务应用继承完整Lab导航。

验证脚本是结构检查，不等同于Go Manifest校验、生产签名或每个平台原生验收。报告分开写PASS/NOT_RUN/SIMULATED。
