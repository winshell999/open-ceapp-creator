# open-ceapp-creator

用于创建、调试和重构 **CanEngine CEAPP** 的开源 Skill、Starter、Demo 与验证工具。

它不是一组静态模板，而是一套面向真实 CanEngine Host Bridge 的 CEAPP 生成工作流：从选择能力范围、生成源码、接入文件 / Runtime / AI / Data / Phone Bridge，到自动验证和最终原生验收，都尽量基于已确认的公开接口，而不是依靠“记忆里的 API 名称”或猜测宿主能力。

> **CanEngine（灿引擎）的当前定位：超级个体的 AI 工作台。**
>
> 它把 AI、文件、应用、数据、设备、算力与可复用工作流放到同一个工作环境中，让个人可以用 AI 调度工具、处理资料、执行任务、调用专业软件和算力，并把成熟流程进一步封装成可重复使用的 CEAPP。

---

## CanEngine：超级个体的 AI 工作台

[CanEngine（灿引擎）](https://hoyee.net/canengine/) 不只是一个 AI 对话框，也不只是一个本地应用容器。

它更像一套面向个人的 AI 工作操作层：AI 可以在用户授权范围内理解当前项目、读取和修改文件、调用本地或远程工具、连接专业软件和算力环境，并把一次性的 AI 操作逐步沉淀为 Skill、Connector、Canvas 工作流或 CEAPP。

对于“超级个体”，重点不是一个人手工完成所有事情，而是让一个人能够：

- 用 AI 理解任务和资料；
- 让 AI 直接操作当前工作目录，而不是只给建议；
- 调用本地软件、远程服务器、GPU 算力和云端模型；
- 把常用方法沉淀成可复用 Skill；
- 把外部 AI 客户端通过 MCP 接入同一个工作现场；
- 把成熟流程封装成 CEAPP，交给自己、团队或客户重复使用。

CanEngine 的设计更强调 **本地工作环境、用户授权、按需连接和低云端依赖**。外部模型、远程服务器和第三方服务可以接入，但不要求所有工作都搬到同一个云端系统中完成。

### CanEngine 的核心组成

| 能力 | 作用 |
|---|---|
| **Canvas** | AI 与用户共同工作的项目空间。文件、代码、素材、任务上下文和产出都可以围绕一个 Canvas 组织。 |
| **Skill** | 把方法、规则、领域知识、工具使用方式和验收标准沉淀为可重复使用的 AI 工作流程。 |
| **MCP Bridge** | 让支持 MCP 的 AI 客户端在授权范围内读取和操作 CanEngine Canvas，而不是只通过复制粘贴交换内容。 |
| **Connector** | 把 AI 接到专业软件、本地 Runtime、远程服务器、算力节点或云端服务，让 AI 不只“回答”，还能调用真实工具完成任务。 |
| **CEAPP** | 把验证成熟的工作流封装成可安装、可重复使用的 CanEngine 应用。 |
| **Host Bridge** | CEAPP 在运行时调用 CanEngine 文件、Job、Runtime、AI、Data、Phone、Notification、Clipboard、Print、Locale 等能力的公开接口。 |
| **Runtime / Jobs** | 通过宿主管理的 Runtime 和 Job 执行受控本地任务，例如声明过的 Python 脚本、文件处理和结果输出。 |
| **Data / Device** | 为 CEAPP 提供本地数据、授权共享数据、Phone Bridge、通知等与个人工作环境相关的能力。 |

### Connector：把 AI 接到真实工具

Connector 是 CanEngine 最近能力扩展的重要方向之一。

它的作用不是再增加一个“聊天入口”，而是把 AI 的操作边界延伸到真实的软件、设备和算力环境。一个 Connector 可以代表桌面软件、服务器、本地运行时、局域网算力或云端模型服务。

当前这类连接方式可以覆盖例如：

- **专业桌面软件**：例如 Blender；
- **开发与协作服务**：例如 GitHub；
- **服务器与基础设施**：例如 SSH 连接器；
- **媒体运行时**：例如 TTS、Remotion；
- **本地 / 局域网 AI 算力**：把独立 GPU 服务器作为 AI 算力节点接入；
- **云端模型服务**：把图像、视频等云端模型能力作为可管理的服务接入。

具体可用连接器取决于当前 CanEngine 环境中实际安装和启用的能力。

这里有一个重要边界：

> **Connector 是 AI 工作台的工具连接层，不等于 CEAPP Runtime 的 Host Bridge。**

AI 能通过 Connector 使用某个工具，并不意味着任意 CEAPP 都可以直接调用同一个 Connector。CEAPP 只能使用当前 CanEngine 明确暴露并授权的公共 Host Bridge。这个区分也是新版 `open-ceapp-creator` 的核心规则之一。

---

## CEAPP 是什么

CEAPP 是运行在 CanEngine 中的应用格式。

一个 CEAPP 可以只是轻量的本地 HTML / CSS / JavaScript 工具，也可以按需加入：

- 本地资源；
- 声明过的 Python 脚本；
- Host-managed Runtime / Job；
- AI 文本、视觉、图片、视频、3D 能力；
- 本地数据或授权共享数据；
- Phone Bridge；
- Notification；
- Clipboard / Print / Locale；
- 文件选择、暂存、打开、导出和结果管理。

**CanEngine 负责宿主、权限、运行环境、AI 配置、数据授权和设备能力；CEAPP 负责把一个明确的业务流程封装成可重复使用的应用。**

CEAPP 不应该绕过 CanEngine 去直接访问内部 Wails / Go 接口、任意 Shell、原始数据库路径或私有 Connector 路由。

---

## open-ceapp-creator 做什么

这个 Skill 的目标是生成 **可以被验证的 CEAPP 源码**，而不是只输出一个看起来像应用的网页。

它当前包含：

- 基于已检查 CanEngine 源码整理的 Host Bridge 契约；
- 可复用的 `ce-bridge.js` Host Adapter；
- AI / Data / Phone 等高层 recipes；
- 9 套可独立运行的 CEAPP Demo；
- 按能力生成项目的 `create_ceapp.py`；
- Manifest / Bridge / UI / Python / Browser 验证工具；
- Runtime / Job 生命周期处理；
- 多状态 UI 和中英文框架；
- 原生 CanEngine 验收清单；
- 打包与签名边界说明。

当前技术快照主要基于 **CanEngine 1.7.3** 的公开 Bridge 与相关实现，于 **2026-09-26** 检查。它是一个源代码基线，不代表每一台已安装 CanEngine 都必然暴露全部相同能力；最终仍以实际安装版本和宿主返回的 capabilities 为准。

---

## 选择最小能力 Profile

新建 CEAPP 时，不建议默认把所有 Bridge 都塞进应用。

`scripts/create_ceapp.py` 提供以下 Profile：

| Profile | 主要能力 |
|---|---|
| `minimal` | 本地 UI、网页打开、Clipboard、Print、Diagnostics |
| `files` | 文件选择、浏览器输入、Staging、目录选择、文件打开 |
| `python` | Files + Python Runtime + Job + Cancel + 结果管理 |
| `ai-text` | Host AI 状态与文本生成 |
| `ai-media` | 文件 + Text / Vision / Image / Video / 3D 生命周期 |
| `data` | App-private 本地数据；按需加入真实 shared dataset / action |
| `phone` | Phone session / receive / import / send |
| `notifications` | 即时通知与宿主通知设置 |
| `full` | 完整 Bridge Lab，用于能力验收，不建议直接作为业务应用 UI |

例如：

```bash
python scripts/create_ceapp.py \
  --app-id my-file-tool \
  --name "My File Tool" \
  --profile python \
  --output /path/to/new-project

python scripts/validate_ceapp.py \
  /path/to/new-project \
  --report /path/to/validation.json
```

如果需要 shared data，必须传入真实存在并已经授权的 dataset / action ID，不要在代码里伪造一个占位资源。

---

## 如何使用这个 Skill

### 方式一：Codex、WorkBuddy 等支持 Skill 的 AI 工具

克隆本项目：

```bash
git clone https://github.com/winshell999/open-ceapp-creator.git
```

将 `open-ceapp-creator` 加入当前 AI 工作环境，然后直接描述要创建或修改的 CEAPP。

例如：

```text
使用 open-ceapp-creator 创建一个图片批量处理 CEAPP。

要求：
- 支持本地选择和 Phone Bridge 导入
- 使用 Python 处理
- 允许取消任务
- 结果可以打开和导出
- 支持中英文
- 最后运行完整验证
```

对于已有项目，也可以直接要求 Skill 根据当前 Host Bridge 规范进行重构和排错。

### 方式二：CanEngine Canvas + MCP

CanEngine 自己也可以作为 AI 工作现场。

典型流程：

1. 创建或打开 CEAPP Canvas；
2. 选择 `open-ceapp-creator`；
3. 通过 CanEngine MCP 把支持 MCP 的 AI 客户端连接到当前 Canvas；
4. AI 读取当前项目和 Skill；
5. AI 直接修改 Canvas 中的 CEAPP 文件；
6. 运行验证；
7. 在 CanEngine 中进行真实 Host Bridge 验收；
8. 打包、签名并导出 `.ceapp`。

这种方式的重点是：**AI 直接工作在项目现场，而不是用户反复复制代码、上传 ZIP、下载文件再手动覆盖。**

MCP 使用说明：<https://canengine.meeinn.com/mcp>

下载 CanEngine：<https://canengine.meeinn.com/download>

---

## 标准项目结构

生成的新项目通常类似：

```text
my-app/
├── app.json
├── index.html
├── app-config.js
├── app.js
├── styles.css
├── assets/
│   ├── ce-bridge.js
│   ├── ceapp-i18n.js
│   ├── recipes.js
│   └── logo.png
├── data/
│   └── localdb.schema.json      # 仅在需要 Data 时存在
└── scripts/
    └── process_file.py          # 仅在需要本地任务时存在
```

其中：

- `app.json`：Manifest、权限、capabilities、commands 和 runtime 声明；
- `app-config.js`：应用级能力配置；
- `ce-bridge.js`：Host Bridge 解析、调用、mutation guard、Runtime / Job 等通用能力；
- `recipes.js`：AI / Data / Phone 等复合流程；
- `ceapp-i18n.js`：`zh-CN` / `en-US` 文案和 Locale 同步；
- `scripts/`：只放 Manifest 明确声明并允许执行的脚本。

---

## Host Bridge 能力地图

CEAPP 通过当前安装的 CanEngine 公共 Bridge 使用宿主能力。

主要能力组包括：

| 能力组 | 典型用途 |
|---|---|
| **Host** | 获取宿主版本、capabilities、能力存在性 |
| **Runtime** | 查询 Runtime 状态、检查 / 请求 Runtime 可用性 |
| **Input** | Native file chooser、浏览器 File / Blob、Staging、原生 Drop |
| **Output** | 打开、Reveal、导出宿主管理的结果文件 |
| **Assets** | 解析 CEAPP 包内资源 |
| **Jobs** | 执行声明过的任务、日志、状态、取消、结果文件 |
| **AI** | Text、Vision、Image，以及 Video / 3D Task 生命周期 |
| **Data** | App-private collection、授权 dataset / action |
| **Phone** | Session、接收、读取、添加、发送文件 |
| **Notification** | 即时通知及按权限启用的计划通知能力 |
| **System** | Clipboard、Print、External URL、Diagnostics、Locale |

完整方法清单见：

- [Manifest 与 Host Bridge](./references/manifest-and-host-bridge.md)
- [Bridge Methods Snapshot](./references/bridge-methods.json)
- [Bridge Recipes](./references/bridge-recipes.md)

---

## 新版 Runtime 规则

### 1. Bridge 必须动态解析

不要假设页面加载时 `window.CanEngine` 一定已经存在。

新版 Adapter 会：

- 延迟解析 Host；
- 处理 parent frame 的跨域访问异常；
- 等待有限时间；
- Host 不存在时显示明确的 Browser Preview 状态；
- 不在浏览器里伪造一次“宿主调用成功”。

### 2. Promise resolve 不等于业务成功

Host 方法可能正常 resolve，但返回：

```json
{"ok": false}
```

因此必须检查每个 domain 自己的返回 envelope，而不是只要没有 throw 就显示“成功”。

### 3. Mutation 不能无脑重试

对以下操作尤其不能在 timeout 后自动再次提交：

- 文件写入；
- 发送到手机；
- Runtime 安装；
- AI 付费生成；
- Video / 3D Task 创建；
- 其他有副作用的操作。

如果结果未知，应先恢复和确认上一笔请求的最终状态，再允许用户再次执行。

### 4. 文件身份必须分清

以下对象不能互相混用：

- Browser `File / Blob`
- `StagedFile.id`
- `StagedFile.path`
- `ChosenDirectory.id`
- `JobInfo.id`
- `ResultFile.fileRef`
- Phone Bridge `fileId`
- AI Task `taskId`

不要根据浏览器 filename 猜 OS 路径，也不要自己构造 `fileRef`。

### 5. Python / Job 由宿主管理

CEAPP 不应该在按钮事件里拼 Shell 命令或临时 `pip install`。

正确方式是：

- 在 `app.json` 声明 Runtime、command、script 和允许参数；
- 提交 Job 前先检查 Runtime；
- 订阅正确的 Job 生命周期；
- 让 Host 管理输入、输出和 Result File；
- 对取消、超时、失败和结果未知分别展示状态。

当前已确认的 Host 行为中，`runJob()` 会等待底层进程结束后再 resolve，因此需要在提交之前订阅完整的 `job:started` 事件，才能在任务执行期间获得可用于取消的真实 Job ID。

详细说明：[Runtime and Jobs](./references/runtime-and-jobs.md)

---

## AI：文本、视觉和媒体任务

CanEngine 负责模型配置、Provider、授权、路由和可能产生的费用。

CEAPP 只通过公开 AI Bridge 发起明确的用户请求。

当前 Skill 覆盖：

- Text；
- Vision；
- Image；
- Video；
- 3D。

其中 Video / 3D 不是“请求后立即得到文件”的同步接口，而是 **Task lifecycle**：

```text
create
→ taskId
→ status / poll
→ success | failed | cancelled
→ result
```

应用需要保存真实 `taskId`、限制轮询时长、允许显式取消，并且在结果未知时避免重复创建可能产生费用的任务。

---

## Data Bridge

本地数据使用：

```js
const store = host.data.local('collection_name')
```

它返回 app-private collection 接口，而不是让 CEAPP 直接执行 SQLite / DuckDB / SQL。

Shared Data 也必须通过明确授权的 dataset / action 使用。应用不能因为 CanEngine 内部使用某种数据库，就假设 CEAPP 自动拥有底层数据库访问能力。

---

## Phone Bridge

Phone Bridge 可以在手机、电脑和 CEAPP 之间传递文件。

典型流程：

```text
创建 / 打开 Phone Session
→ 手机上传
→ 获得 Phone fileId
→ readFile() 得到 Blob
→ stageFile()
→ 进入 CEAPP 的文件 / Python / AI 工作流
```

Phone `fileId` 与普通 Staged File ID 不是同一种对象。

发送到手机属于有副作用的动作，应在 CEAPP UI 中做明确的用户确认，不要依赖一个宿主可能忽略的请求字段。

详细说明：[Phone Bridge](./references/phone-bridge.md)

---

## 文件、网页、Clipboard 与 Print

### 文件

推荐把不同输入来源归一到同一处理流程：

```text
Native chooser ──┐
Browser picker ──┤
Paste ───────────┤
DOM drop ────────┤
Native drop ─────┼→ normalize / stage → validate → workflow
Phone Bridge ────┘
```

大文件优先使用 Host Native File Selection，避免把大型媒体转成 Base64 塞进 WebView。

### 外部网页

使用公开的：

```js
await host.openExternalURL('https://example.com')
```

只允许经过校验的 HTTP(S) 地址，不要猜测 `openURL`、`openExternal` 等不存在的方法。

### Clipboard / Print

Clipboard 要区分 Text、Image 和 File。

Print 应只打印可信或经过转义的 HTML。弹出打印窗口不等于打印机已经成功完成输出。

---

## 标准 UI

新版 Starter 的 UI 定位是 **桌面工作工具 / Workbench**，不是营销落地页。

默认要求：

- 本地 HTML / CSS / JS；
- 无 CDN 首屏依赖；
- System Font；
- Light / Dark；
- 1440 / 768 / 390px 响应式；
- 清晰的 Loading / Empty / Error / Disabled / Success / Cancelled / Unknown 状态；
- 重复提交保护；
- Host 不存在时显示 Browser Preview；
- 中英文文案集中管理；
- 不把未完成的宿主动作伪装成成功；
- 用户 / AI 返回文本默认使用 `textContent`，避免不受控 HTML 注入。

对于真实业务应用，应保留一条清晰主流程。完整九面板 Bridge Lab 是能力验收工具，不应原样复制成所有客户应用的 UI。

详细说明：[Standard UI](./references/standard-ui.md)

---

## 9 套可运行 Demo

`assets/demos/` 当前包含：

| Demo | 用途 |
|---|---|
| `minimal` | 基础宿主、网页、Clipboard、Print、Diagnostics |
| `files` | File choose / stage / open / export |
| `python` | Runtime、Job、Python、结果与取消 |
| `ai-text` | Text AI |
| `ai-media` | Vision / Image / Video / 3D |
| `data` | App-private Data |
| `phone` | Phone Bridge |
| `notifications` | Notification |
| `full` | 完整 Bridge Lab |

每个 Demo 都是独立 CEAPP 源码目录。

不要把整个 `assets/demos/` 父目录当成一个 CEAPP 打包。

更多说明：[Demo Catalog](./references/demo-catalog.md)

---

## 验证

新版 Skill 不把“代码能打开”当作“CEAPP 已完成”。

### 自动验证

在 Skill 根目录运行：

```bash
node --test tests/bridge.test.cjs

python tests/test_tools.py

python scripts/audit_contract.py assets

python scripts/validate_ceapp.py \
  /path/to/generated-app \
  --report /path/to/validation.json
```

如果修改 UI，并且本机安装了 Playwright + Chromium：

```bash
python tests/browser_smoke.py \
  --app assets/starter \
  --out /path/to/browser-results
```

Browser Smoke 只能证明浏览器层 UI 和模拟流程，不等于真实 CanEngine Host Bridge 已通过。

### 证据状态

验收结果使用：

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT_RUN`
- `SIMULATED`

不能把 Browser Mock、Fixture 或静态检查写成 Native PASS。

### 原生验收

涉及的真实能力仍应在实际安装的 CanEngine 中测试，例如：

- Package / Sign / Install；
- Native file choose / cancel / drop；
- File open / reveal / export；
- Runtime 缺失与安装；
- Python success / fail / cancel；
- AI disabled / configured / timeout；
- Local / Shared Data；
- Phone receive / send；
- Notification；
- Clipboard / Print；
- Locale / Theme；
- Packaged Media。

完整清单：[Testing and Acceptance](./references/testing-and-acceptance.md)

---

## 技术边界

为了避免“浏览器里看起来能跑，装进 CanEngine 就失败”，新版 Skill 明确禁止以下做法：

- 不根据印象发明 Host API；
- 不直接访问 `window.go`、`window.runtime` 等内部实现；
- 不把 AI Connector 当作 CEAPP Runtime API；
- 不从浏览器 filename 推导本地绝对路径；
- 不在前端拼接并执行任意 Shell；
- 不执行用户随手选择的任意脚本；
- 不在点击事件中临时安装 Python Package；
- 不绕过被拒绝的权限改走 raw path；
- 不在超时后自动重试付费 / 发送 / 安装操作；
- 不伪造 `fileRef`、`jobId`、`taskId`；
- 不生成官方 / KOL 签名或伪造可信身份；
- 不声称浏览器测试等于原生验收。

---

## 项目结构

```text
open-ceapp-creator/
├── .github/
├── agents/
│   └── openai.yaml
├── assets/
│   ├── demos/                         # 9 套独立 CEAPP Demo
│   ├── recipes/
│   │   └── advanced-bridges.js
│   └── starter/                       # 完整 Bridge Lab / Starter
├── references/
│   ├── source-baseline.md
│   ├── manifest-and-host-bridge.md
│   ├── bridge-methods.json
│   ├── bridge-recipes.md
│   ├── runtime-and-jobs.md
│   ├── phone-bridge.md
│   ├── standard-ui.md
│   ├── bilingual-framework.md
│   ├── offline-runtime.md
│   ├── demo-catalog.md
│   ├── testing-and-acceptance.md
│   ├── troubleshooting.md
│   └── packaging-and-signing.md
├── reports/
├── scripts/
│   ├── create_ceapp.py
│   ├── validate_ceapp.py
│   └── audit_contract.py
├── tests/
│   ├── bridge.test.cjs
│   ├── browser_smoke.py
│   └── test_tools.py
├── SKILL.md
├── README.md
└── LICENSE
```

---

## 打包与签名

这个仓库生成的是 **CEAPP Source**，不是已经获得官方 / KOL 信任身份的安装包。

完成验证后：

1. 打开 CanEngine；
2. 进入 CEAPP 打包 / 签名能力；
3. 选择 **单个生成后的 CEAPP 根目录**；
4. 由 CanEngine Client 完成结构检查、打包和当前授权身份签名；
5. 安装输出结果；
6. 完成真实 Native Acceptance。

不要把整个 Skill 仓库、`assets/demos/` 父目录、`tests/` 或备份目录一起拖进 CEAPP 打包器。

签名来源和运行正确性是两个不同问题：能够签名，不代表所有 Runtime / AI / Phone / OS 行为都已经通过验收。

详细说明：[Packaging and Signing](./references/packaging-and-signing.md)

---

## 参考文档

- [Verified Source Baseline](./references/source-baseline.md)
- [Manifest 与 Host Bridge](./references/manifest-and-host-bridge.md)
- [Bridge Methods Snapshot](./references/bridge-methods.json)
- [Bridge Recipes](./references/bridge-recipes.md)
- [Runtime and Jobs](./references/runtime-and-jobs.md)
- [Phone Bridge](./references/phone-bridge.md)
- [Standard UI](./references/standard-ui.md)
- [Bilingual Framework](./references/bilingual-framework.md)
- [Offline Runtime](./references/offline-runtime.md)
- [Demo Catalog](./references/demo-catalog.md)
- [Testing and Acceptance](./references/testing-and-acceptance.md)
- [Troubleshooting](./references/troubleshooting.md)
- [Packaging and Signing](./references/packaging-and-signing.md)

---

## License

本项目使用 [MIT License](./LICENSE)。
