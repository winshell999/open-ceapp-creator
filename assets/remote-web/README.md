# 远程网站示例 · 1.8.0

需要包含远程网站嵌入实现的CanEngine 1.8.0构建。macOS需要14+；Windows使用WebView2 Runtime（amd64）。版本保持1.8.0。

这是公开的通用模板，`https://example.com/app/`为占位地址。生成时提供自己的固定网站入口和appId；应用仅包含公开声明、本地图标和说明，无需本地HTML、Python或占位命令。网站直接显示在CanEngine主窗口右侧。

默认未启用网站授权保护。需要仅通过CanEngine访问时，在`runtime.remoteWeb`中添加`"authorization": "canengine"`，最低宿主为包含此功能的1.8.0构建。还需在授权中心登记相同appId和入口，并在网站服务端验证启动票据。声明本身不能阻止普通浏览器访问；网站密钥、授权码、License Token和服务端PHP不得放进CEAPP目录。

`persistent`按appId保存独立网站数据；`ephemeral`在关闭时丢弃数据。切换应用保留页面，普通刷新遵循网站行为。缓存服从网站的Cache-Control，不保证离线启动或业务数据持久化。启用保护后的新启动始终在线申请新票据，不凭旧Cookie跳过检查。

默认顶层导航仅允许入口origin。跨域登录需声明精确`allowedOrigins`并实际验收。远程页面没有Host Bridge；网站内容和语言由网站决定。

通过CanEngine的CEAPP打包与签名界面使用自己的合法开发者身份打包。更改入口、授权声明或其他包内配置后，重新打包和签名；不要自行更改版本号。
