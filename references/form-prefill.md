# 网站 → 快速预填 CEAPP · CanEngine 1.8.0

## 入口与产出

用户可以只提供“网站地址 + open-ceapp-creator + 做成快速预填 CEAPP”。Agent负责字段调研、JSON映射、业务界面、源码生成、验证和实际CanEngine验收；不要把调研工作转交给用户。沿用已有项目身份和SQLite结构。新应用默认一个固定目标、双语本地界面、内存输入、不新增数据库；用户要求保存资料时才增加受控持久化。应用版本独立于宿主版本。

选择`form-prefill`，应用本身使用`runtime.web`。本地界面经宿主Bridge调用原生网站视图，在右侧官网预填；官网没有Host Bridge。`runtime.remoteWeb`只是联网网站运行模式，没有调用预填的本地Bridge。修改app.json是能力声明，不能替代宿主实现。

默认交付：干净源码、脱敏字段映射、验证报告、分平台原生验收记录。需要可安装包时走授权的CanEngine打包/签名流程；不要制造签名身份或把私钥放进项目。

## 1. 调研实际网站

通过作者环境中可用的浏览器/网页工具访问用户指定的真实页面，遵守页面认证和正常访问流程。观察运行后的DOM和联动行为；服务端HTML只能作为补充。不要绕过登录、TLS、验证码或网站访问控制。URL不是字段证据，也不能由AI记忆里的旧结构直接生成生产映射。

在应用包外保存`field-map.json`或同等报告，记录调研时间、固定页面、字段业务含义、DOM证据和如下内容，排除真实值、Cookie、令牌、整页HTML及网络请求正文：

| 项目 | 必须核对 |
|---|---|
| scope | 实际页面中唯一的form/容器；不能用整个body掩盖定位歧义 |
| selector | scope内恰好一个控件，优先稳定ID/name；不使用脆弱nth-child猜测 |
| kind | 真实原生控件类型；readonly text日期仍是text，不能改写为date |
| 格式 | 网站日期、大小写、长度、电话国家码等约束；禁止把护照号码转为数字 |
| select | 唯一option.value及其人类标签；不要猜测文本、国家代码或模糊匹配 |
| dependencies | 上级字段变化如何更新下级选项，已验证的事件及依赖顺序 |
| 保护/支持性 | 验证、同意、隐藏、密码、文件、提交控件剔除；非标准组件标记手工 |

默认不派发事件。需要联动/框架状态时，确认input/change/blur不会触发自动保存或业务提交，再显式声明。作者调研可以使用开发浏览器的DOM工具；**CEAPP运行时没有公开的browser.query/readDOM/evaluate接口**，不能把作者工具或宿主内部DOM适配器当成CEAPP API。

页面不可访问时先完成本地界面和结构校验，并明确标记映射/网站验收BLOCKED或NOT_RUN；保留未配置状态，禁止伪造selector并声称自动填写成功。已经明确的目标无需重复请求授权，网站域名许可由CanEngine的原生权限流程处理。

## 2. 固定目标与公共接口

在本地Web应用的签名manifest中声明：

```json
{
  "minCanEngineVersion": "1.8.0",
  "permissions": ["browser.form.prefill"],
  "capabilities": {
    "browser": {
      "profiles": ["form-prefill-v1"],
      "targets": [{"id": "registration", "url": "https://forms.example.com/register"}]
    }
  }
}
```

这个域名只是协议示例，不能用于生产映射。每个应用允许1–16个明确HTTPS页面，ID为字母开头的字母/数字/下划线/连字符，最多64字符。Host小写，无凭据、通配符或反斜杠；URL最多2048 UTF-8字节。固定页面可有网站本身要求的静态query，但绝不附加姓名、证件、邮件、住址等数据。原生批准会列出页面；manifest变化会使旧批准失效。不要添加浏览器通配权限、任意allowedOrigins或调用者提供的运行时URL。

```js
const result = await window.CanEngine.browser.prefill(request); // JSON对象或JSON字符串
await window.CanEngine.browser.openTarget('registration');     // 仅打开已声明目标
const state = await window.CanEngine.browser.getStatus('form-prefill-v1');
await window.CanEngine.browser.close('form-prefill-v1');
```

运行时请求只引用本应用target ID。实例身份由宿主Bridge提供，不能由CEAPP指定其他appId/viewId。导航锁定精确origin，DOM操作进一步锁定完整目标URL和原生document ID；跳转、所属应用关闭、后端退出、权限撤销都会中止操作。不同目标切换销毁旧会话。预填视图使用临时独立浏览器存储，不继承remoteWeb的persistent选项。

首次调用前有界等待注入，判断方法存在；这不等于权限、配置和网站已就绪。缺失接口显示需要匹配1.8.0+宿主，不降低最低版本，不改用外部浏览器或Tampermonkey。

## 3. JSON映射

下例仅解释形状；每个selector、kind、value编码和事件都必须替换为调研所得内容：

```json
{
  "schemaVersion": 1,
  "target": "registration",
  "scope": "form#registration",
  "fields": [
    {"key":"fullName","selector":"#fullName","kind":"text","value":"TEST USER"},
    {"key":"email","selector":"#email","kind":"email","value":"test@example.invalid"},
    {"key":"country","selector":"#country","kind":"select","value":"SGP","events":["change"]},
    {"key":"city","selector":"#city","kind":"select","value":"SINGAPORE","dependsOn":["country"]}
  ]
}
```

| 属性 | 契约 |
|---|---|
| schemaVersion | 整数1；请求没有任意脚本/URL或额外属性 |
| scope/selector | 非空CSS selector，各最多512 UTF-8字节，不含NUL/换行；实际唯一性由原生DOM预检查核对 |
| fields | 1–64个，整个请求最多64 KiB；key唯一，格式同target ID |
| kind | text/search/email/tel/number/url/date/datetime-local/time/month/week/textarea/select/checkbox/radio |
| value | 字符串最多8192 UTF-8字节，无NUL；checkbox/radio必须JSON布尔值 |
| match | 默认exact；case-insensitive只用于已知大小写标准化，不适用于toggle |
| dependsOn | 最多16个已知、唯一前置key，无自依赖和循环 |
| events | 默认为空；仅允许唯一input/change/blur，绝无click、submit或任意事件 |

select用唯一option.value，date用YYYY-MM-DD；网站text日期遵守实际格式。checkbox/radio只有普通业务控件可填，验证码、身份验证、同意条款和最终提交绝不包含在映射中。跨域iframe、Shadow DOM、自定义下拉、canvas和特殊流程需要手工处理或另外审查的宿主适配器；不得宣称支持任何网站所有控件。

## 4. 生成和定制

先把真实调研映射以**虚构值**写入包外的`reviewed-request.json`，再执行：

```bash
python scripts/create_ceapp.py --profile form-prefill \
  --app-id my-registration --name "登记预填" \
  --url 'https://THE-ACTUAL-HOST/ACTUAL-PAGE' \
  --mapping /path/to/reviewed-request.json --output /path/to/new-app
python scripts/validate_ceapp.py /path/to/new-app --report /path/to/validation.json
```

生成器要求显式URL和已调研JSON，不负责联网猜字段，拒绝覆盖现有目录和额外origin。当前用户指定宿主、skill与全部模板版本为1.8.0；新应用默认version和minCanEngineVersion均为1.8.0，既有项目未经明确指示不得改号。`assets/form-prefill`原始模板没有目标/映射，不能直接签名交付。

本地stdlib后端只提供健康检查与白名单静态资源，日志关闭、所有响应no-store，用户输入不会发给该后端。界面根据映射生成输入，值只通过内存Host Bridge交付。`assets/form-config.json`中：

- request：公共JSON结构；生产默认值改为空字符串/必要的无敏感默认项，测试fixture留在包外。
- titleI18n、labels[key]、formatHints[key]：zh-CN/en-US文案，跟随宿主语言。
- options[key]：`[{"value":"已核对的编码","label":{"zh-CN":"中文标签","en-US":"English label"}}]`；补齐后用户选人类标签。

生成后必须定制业务界面和所有字段标签/格式，不交付只显示机器key/原始编码的半成品。根据需要做旅客/客户选择、日期联动、输入校验，保持一个聚焦操作；不要复制完整Bridge Lab。

已有SQLite应用沿用原表、主键、旅客管理和调用入口，在选定记录的本地接口中构造fields.value。后端使用CANENGINE_APP_DATA_DIR；禁止打包真实SQLite或硬编码开发机数据库路径。敏感接口使用现有身份验证、同源/CSRF检查和no-store；只返回所选记录必要字段。不得新建URL token/数据库交接表、调试日志、剪贴板或localStorage副本来传递旅客信息。只有用户明确要求的资料保存才是必要持久化。

## 5. 加载、回读和降级

Host有35秒总时限；ready后最多8秒进行无值DOM预检查。先核对scope和所有控件；缺失可等待，受保护/歧义/禁用等立即降级。依赖批次先设置全部兄弟字段，再发送明确事件；前批回读稳定一秒再进入下批，在有界时间内等待选项。已成功字段不会反复重放，最终逐字段稳定回读；更晚的异步重置或用户修改需要人工处理。

结果：`{ok, filled, code, fields:[{field,status}], manualRequired:true}`。成功仍需用户审阅；`ok:false`必须显示待处理字段，不能绿色“已完成”。code为FORM_CHANGED/DOMAIN_DENIED/MANUAL_REQUIRED等受控码；字段状态包括filled、missing、ambiguous、blocked、protected、option-missing、mismatch、invalid。不要显示值、HTML、Cookie、selector或原始异常正文。

宿主也可能拒绝Promise，使用已知BROWSER_*码生成本地双语提示。单次操作期间禁用重复填写/打开。未知Bridge超时保留锁，先查询getStatus并核对官网；只有确定前一操作结束才允许用户重试，禁止自动重发。模板采取保守锁定并提示核对后重开。结构变更时保留官网供人工补填，更新映射需重新调研；不得放宽scope、模糊选择或偷偷改用任意JS。

预填期间原生层阻止导航型意外提交和新窗口，完成后恢复正常人工操作。网页AJAX业务行为无法仅凭DOM辨认，因此不能许诺“任意事件均不会提交”；未知网站保持events为空，必需事件须实测。Agent与CEAPP都不能破解/代填验证码或点击最终提交。

## 6. 验收与交付

1. 跑全skill回归及`tests/test_prefill.py`：版本/权限/目标、类型/尺寸/依赖/事件、生成拒绝、敏感值脱敏、真实本地HTTP白名单。
2. 跑`tests/prefill_browser_smoke.py`：真实本地服务器，离线首屏、双语/明暗/窄屏、字段值、重复操作、负结果、未知超时锁、dispose。Bridge模拟结果只记SIMULATED。
3. 在实际安装的CanEngine签名/安装/打开新应用，使用虚构资料访问目标官网。核对右侧原生视图、预填每项回读、用户编辑、切换返回、刷新、网页变化/无匹配、安全字段拒绝、域名/目标拒绝、所属应用关闭。不要提交测试登记、尝试验证码或对真实资料作自动测试。
4. 检查业务值未进入URL、日志、持久化status、app_data交接文件/副本；若资料管理是用户要求，验证原SQLite数据与schema保留。测试只输出字段名/状态/计数。
5. 每层写PASS/FAIL/BLOCKED/NOT_RUN/SIMULATED；macOS14+ WKWebView与Windows amd64/WebView2分开。编译通过不等于Windows实机通过。随源码附脱敏映射、依赖、宿主要求、操作说明、已跑结果和待验收项。

此前临时编号构建在实际macOS CanEngine中对MDAC虚构资料完成22/22预填、人工修改、返回保留、刷新清空、保护字段拒绝及所属应用关闭；Windows完成编译，实机NOT_RUN。历史结果及原始编号保存在source-baseline.md和报告中，不代表重新验收1.8.0或其他网站。当前版本由用户明确指定为1.8.0；当前构建/校验见../reports/VERSION_1_8_0_VALIDATION_REPORT.md。MDAC专用browser.open/fill及SQLite调用保留，新项目优先使用通用JSON接口。
