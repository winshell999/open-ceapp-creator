# open-ceapp-creator

用于创建 **CanEngine CEAPP 源码项目** 的开放版 Skill 与基础模板。

它可以帮助开发者、创作者和 KOL 生成符合 CanEngine 规范的应用目录，包括 `app.json`、HTML、CSS、JavaScript、本地资源、双语支持以及 Host Bridge 接入代码。项目完成后，可在 CanEngine 中校验、打包和签名，最终导出 `.ceapp` 应用包。

> 本仓库只负责生成 CEAPP 源码项目，不提供 CanEngine 官方或 KOL 私钥，也不会直接生成带官方或 KOL 身份的最终发行包。

## 说明

**CanEngine 用来统一运行和管理个人 AI 应用，CEAPP 则把已经验证有效的 AI 流程、网页工具和本地自动化任务封装成可以反复使用的应用。**

- CanEngine 解决“应用在哪里运行、如何连接 AI、本地文件和不同设备”的问题。
- CEAPP 解决“如何把一次性操作沉淀成稳定工具”的问题。

## CanEngine 是什么

[CanEngine（灿引擎）](https://hoyee.net/canengine/) 是一个连接 AI、电脑文件、个人应用和不同终端的本地工作空间。

它不只是一个 AI 对话工具，而是让 AI 在用户授权范围内读取项目上下文、处理本地文件、修改网页或代码，并把结果继续沉淀为可重复使用的应用和工作流。

CanEngine 的主要能力包括：

- **Apps**：统一安装、管理和运行个人应用，把重复工作沉淀为工具。
- **Canvas**：承载网页、代码、文档、图片和项目文件，让 AI 直接参与修改。
- **AI Bridge**：由 CanEngine 统一管理模型配置、API Key、权限和调用，CEAPP 不需要自行保存密钥。
- **MCP Bridge**：连接 ChatGPT\Gemini 等支持 MCP 的 AI 客户端，让 AI 在授权范围内读取和操作画布。
- **Phone Bridge**：在手机与电脑之间传递图片、文档、文字和临时素材。
- **Notification Bridge**：让应用发送即时通知或创建计划通知。
- **Data Bridge**：为应用提供本地数据和受控的数据访问能力。

产品介绍：<https://hoyee.net/canengine/>

下载 CanEngine：<https://canengine.meeinn.com/download>

## CEAPP 是什么

CEAPP 是运行在 CanEngine 中的应用格式。它既可以是一个简单的 HTML 工具，也可以包含 JavaScript、Python、Node.js、本地资源，以及 CanEngine 提供的 Host Bridge 能力。

一个标准 CEAPP 项目通常包含：

```text
MyApp/
├── app.json
├── index.html
├── styles.css
├── app.js
├── assets/
└── scripts/       # 需要本地命令或后端能力时使用
```

开发完成后，项目需要通过 CanEngine 校验并打包为 `.ceapp` 文件。

## CEAPP 可以解决什么问题

### 1. 把一次性的 AI 对话变成可重复使用的工具

很多 AI 结果只停留在聊天窗口中。下次执行同类任务时，还要重新解释需求、上传文件、组织提示词和调整输出格式。

CEAPP 可以把已经验证有效的流程封装成应用，让用户通过固定界面直接使用，不需要每次从头开始。

### 2. 把分散的个人应用统一管理起来

使用 AI 生成的网页、脚本和小工具通常散落在不同目录、平台或开发环境中，后续很难查找、维护和复用。

CEAPP 将应用的代码、资源、版本、权限和运行入口放在统一结构中，再由 CanEngine 集中安装和管理。

### 3. 连接本地文件和桌面工作流

普通网页很难稳定访问本地文件、目录、运行环境和桌面能力。

CEAPP 可以通过 CanEngine 提供的受控 Bridge 读取文件、执行任务、调用 AI、导出结果，同时保留明确的权限边界。

### 4. 减少重复开发

CEAPP 可以复用 CanEngine 已经提供的 AI、文件、通知、数据和手机互传能力。开发者不需要在每个应用里重复实现：

- API Key 管理
- 模型接入
- 文件上传与导出
- 手机和电脑之间的素材传递
- 通知系统
- 本地数据存储

### 5. 支持本地运行和离线优先

CEAPP 可以把 HTML、CSS、JavaScript、图片和字体等资源放在应用包内。

对于不依赖在线服务的功能，即使没有网络，应用仍然可以启动和使用；需要调用在线 AI 服务时，再由 CanEngine 统一处理连接和授权。

### 6. 让应用可以持续维护和升级

每个 CEAPP 都有独立的应用 ID、版本、权限声明、运行环境和发布者身份。

相比散落的脚本或临时网页，CEAPP 更适合长期维护、版本升级和统一分发。

## 官方、KOL 和自签 CEAPP 的区别

CanEngine 会根据签名身份标识应用来源，并限制应用是否可以分享给其他用户。

| 类型 | 签名身份 | CanEngine 标识 | 是否可以分享给别人使用 | 适用场景 |
|---|---|---|---|---|
| **官方 CEAPP** | 由 CanEngine 官方身份签名 | 绿色“官方”标签 | **可以** | CanEngine 官方发布和维护的应用 |
| **KOL CEAPP** | 由 CanEngine 授权的 KOL、创作者、机构或合作伙伴身份签名 | 蓝色发布者名称标签 | **可以** | 经过平台授权的发布者向其他用户分发应用 |
| **自签 CEAPP** | 由普通用户使用自己的本地开发者身份签名 | 黄色用户名称标签 | **不可以** | 个人开发、测试和自己使用的应用 |

### 重要安全规则

- **官方 CEAPP 和 KOL CEAPP 可以分享给其他 CanEngine 用户使用。**
- **自签 CEAPP 只能由签名者自己使用，不能分享给其他用户使用。**
- 自签限制不是功能缺失，而是安全边界：它可以降低未知代码通过个人签名在用户之间传播的风险。
- 需要对外分享的应用，应通过 CanEngine 官方或经过授权的 KOL 发布者身份进行签名和发布。

> 签名用于识别应用来源、检查应用包是否被修改，并向用户提示风险等级。签名不等于对应用代码进行了完整安全审计，用户仍应确认应用申请的权限是否合理。

CanEngine 还可能显示以下状态：

- **未签名**：灰色标签，无法确认应用来源。
- **签名无效**：红色标签，应用包可能在签名后被修改，不应继续使用。

## CEAPP 创建与发布流程

1. 使用本 Skill 创建或修改 CEAPP 源码项目。
2. 确认项目根目录至少包含 `app.json` 和 `index.html`。
3. 确认 CSS、JavaScript、图片、字体等关键资源均保存在项目目录中。
4. 打开 CanEngine。
5. 进入 `我的 → 开发者身份 / CEAPP打包与签名`。
6. 将 CEAPP 项目根目录拖入打包区域。
7. CanEngine 校验项目，并根据当前开发者身份完成打包和签名。
8. 导出最终的 `.ceapp` 文件。
9. 官方或 KOL 签名的 CEAPP 可以分享给其他用户；自签 CEAPP 仅供本人使用。

## 本仓库包含什么

```text
open-ceapp-creator/
├── assets/starter/                 # CEAPP 基础模板
├── references/                     # 开发、Bridge、离线和签名规范
├── SKILL.md                        # Skill 主说明
├── README.md
└── LICENSE
```

`assets/starter/` 默认采用本地 HTML、CSS 和 JavaScript，不依赖远程 CDN，并提供双语、AI Bridge 和 Notification Bridge 的基础示例。

## License

本项目使用 [MIT License](./LICENSE)。
