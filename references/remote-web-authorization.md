# 受保护远程网站声明 · CanEngine 1.8.0

用于“只允许在CanEngine中使用、别人拿到网址也打不开”的网站应用。使用`runtime.remoteWeb`，加入`authorization: "canengine"`，并由网站服务端验证启动票据。普通远程应用不声明此字段。远程网页仍没有Host Bridge；不要把受保护网站套进本地HTML、跨域iframe或伪造浏览器标识。

## 公开声明

```json
{
  "schemaVersion": 1,
  "appId": "protected-web-demo",
  "name": "Protected Website",
  "nameI18n": {"zh-CN": "受保护网站", "en-US": "Protected Website"},
  "description": "Requires a valid formal CanEngine license and internet access.",
  "descriptionI18n": {"zh-CN": "需要有效正式CanEngine授权和网络。", "en-US": "Requires a valid formal CanEngine license and internet access."},
  "version": "1.8.0",
  "minCanEngineVersion": "1.8.0",
  "platforms": [{"os": "darwin", "arch": "*"}, {"os": "windows", "arch": "amd64"}],
  "runtime": {
    "remoteWeb": {
      "url": "https://example.com/app/index.php/",
      "storage": "persistent",
      "authorization": "canengine"
    }
  },
  "permissions": ["web.network"]
}
```

`example.com`与appId都是公开示例，占位地址不会自动获得授权。创建实际应用时使用已登记的appId和完全一致的固定入口，appId需2–64字符。包无需`entry`、本地HTML、PHP、命令或执行环境，也不声明网站服务端密钥。可选`allowedOrigins`沿用精确origin规则。

需要包含该授权实现的CanEngine 1.8.0构建；同版本旧二进制不会因增加字段而获得功能。此skill、新项目与模板默认版本保持1.8.0；已有应用版本保持原值，不自动升到1.8.1。

```bash
python scripts/create_ceapp.py --profile remote-web --authorization canengine \
  --app-id protected-web-demo --name "Protected Website" \
  --url https://example.com/app/index.php/ --storage persistent \
  --output /path/to/new-protected-app
python scripts/validate_ceapp.py /path/to/new-protected-app
```

这两个命令生成并检查公开CEAPP源码，不登记网站、不获取密钥，也不证明网站已受保护。随后使用用户自己的合法开发者身份打包签名；声明变更后重新签名，核对实际交付包内的最低版本。

## 极简PHP首页与固定握手

网站登记绑定appId、入口URL和受保护路径，网站持有独立服务端密钥。所有有效正式CanEngine授权码均可使用所有登记的受保护应用，体验用户不能使用；不增加逐应用、套餐或MCP授权限制。

小PHP应用优先交付一个首页文件：在HTML输出前执行授权校验，失败立即返回错误，成功后再显示首页。PHP及配置留在网站，不复制到CEAPP/skill模板。不要为了示例要求用户配置环境变量或部署多层目录；实际秘密可按网站现有的私有配置方式保存。

如果已验证服务器支持PHP的PATH_INFO，可以用同一个`index.php`处理：

| 用途 | 示例 |
|---|---|
| CEAPP固定入口 | `https://example.com/app/index.php/` |
| 登记受保护路径 | `/app/index.php/` |
| 票据POST地址 | `https://example.com/app/index.php/__ceapp__/launch` |

这是一个PHP文件，不是`index.php`目录；末尾斜杠需与登记值一致。先验证服务器确实执行该PHP及PATH_INFO路径，再采用此形式，不要假定所有PHP主机均支持。已有路由的站点也可保留自己的统一入口，让`<受保护路径>/__ceapp__/launch`进入校验代码。

启动流程：CanEngine用自己的License Token向授权中心`POST /api/v1/canengine/remote-web/launch-ticket`申请票据；原生WebView以表单POST提交`ticket`；PHP用网站密钥在服务端调用`POST /api/v1/canengine/remote-web/verify`，发送`app_id`和`ticket`，密钥放在`X-CanEngine-App-Key`头。PHP确认响应中的授权结果、appId、固定入口、授权记录及期限，建立本地授权会话，并303回到固定入口。

网站无须取得用户的授权码或长期License Token。票据有效60秒、只能使用一次；API兑换时复核当前授权、项目和设备状态。票据不得进入URL、页面JS、通用RPC、日志或跨域POST。

每次关闭重开都在线申请新票据，切换/恢复视图与普通刷新复用会话。网站会话固定最长8小时，并受授权码到期时间限制；不能按每次访问滑动延长。停用后的新启动拒绝，已建立的会话可用至原期限。新的握手失败必须清空旧授权，不能用旧Cookie或缓存页面完成启动。授权中心故障返回503，无授权请求返回403。

Cookie限制网站和路径，使用Secure、HttpOnly与SameSite=Lax；所有受保护响应使用`Cache-Control: no-store, private`。只给首页加校验不会保护绕过PHP的业务API或直接提供的静态资源，实际受保护请求需经过同一服务端校验入口。User-Agent、前端JS、来源页判断和CEAPP签名本身都不能代替这一步。

## 开源与验证边界

- 公开skill、模板和报告使用保留示例域名、虚构appId与合成数据。实际网站密钥、管理员Token、License Token、授权码、票据、Cookie、设备/客户身份、私有绝对路径和未脱敏截图不进入开源文件或ZIP。
- CEAPP仅包含网站入口、公开声明及本地图标。不要把网站PHP、`.env`、授权会话、数据库或密钥文件放入待打包目录。生成器不接受网站密钥参数；校验器拒绝不支持的声明字段及网站服务端文件，但这不替代对任意文件的人工隐私检查。
- 源码校验、接口/HTTP测试和macOS/Windows原生验收分别记录。至少验证无Cookie拒绝、有效正式授权成功、体验/过期/停用/设备拒绝、票据重放/跨应用失败、旧Cookie不能绕过失败启动及固定会话期限。只做声明校验不得写成原生握手PASS。

首版防止仅凭网址访问，不承诺对抗客户端凭据提取、会话复制或前端代码下载。
