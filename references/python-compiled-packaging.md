# Python编译发布 · CanEngine 1.8.0

用于CanWeChat这类常驻Python本地网站。源码项目保持可维护的Python结构，根目录的`ceapp.build.json`只启用可选编译能力。默认“普通打包”保留源码、资源及原有平台声明，不检查/安装编译工具。显式选择“源码保护打包（高级）”才先编译，再发布原生后端及明确列出的静态资源。没有有效配置或配置不支持当前平台时，仍可普通打包。

需要包含此实现的CanEngine **1.8.0构建**。宿主版本、应用版本及appId各自独立，不因添加编译配置自动变更。旧的1.8.0二进制不会仅靠manifest获得打包功能。

## 创建或迁移

```bash
python scripts/create_ceapp.py --profile web-python --compile-python \
  --app-id my-python-web --name "My Python Web" --output /path/to/new-source
python scripts/validate_ceapp.py /path/to/new-source --report /path/to/validation.json
```

迁移已有项目时保留`app.json`、前端、业务代码、目录授权和签名边界。当前支持`runtime.web`、空`commands`、从项目根用Python启动的脚本（`args`第一项为入口），运行时需求仅限base-runtime/python-runtime。离散Python Job、远程网站和额外托管运行时不在这项编译功能的范围内。

配置示例（平台必须与项目已有支持及原生依赖一致，不能仅添加Windows目标就声称CanWeChat已完成Windows迁移）：

```json
{
  "schemaVersion": 1,
  "python": {
    "entry": "run_demo.py",
    "sourcePaths": ["src"],
    "includePackages": ["canwechat"],
    "outputName": "canwechat-server"
  },
  "assets": ["frontend", "assets", "vendor"],
  "targets": [{ "os": "darwin", "arch": "arm64" }]
}
```

纯标准库模板可声明darwin/arm64、darwin/amd64、windows/amd64，输出由当前系统和架构决定。Mac和Windows共用这份schema及Go构建逻辑，但须分别构建，不能在Mac编译Windows原生包。Windows输出自动添加`.exe`；单平台发布只声明本机，多平台发布可合并实际导出的产物。

所有路径采用项目内POSIX相对路径，不允许绝对路径、父目录逃逸、`.`、开发机路径或外部符号链接。`sourcePaths`是本地Python包搜索目录；`includePackages`用于把业务包及子模块明确交给编译器，尤其是动态导入。`assets`是发布资源白名单，不是源码目录列表。`app.json`、`ceapp.build.json`、`ceapp.native.json`和`backend`为保留目标，业务.py、字节码、C源码、头文件及私钥不能作为发布资源。

## 后端适配

```python
ROOT = Path(os.environ.get("CANENGINE_APP_DIR") or Path(__file__).resolve().parent).resolve()
DATA = Path(os.environ.get("CANENGINE_APP_DATA_DIR", str(ROOT / ".local-data")))
host = os.environ.get("CANENGINE_HOST", "127.0.0.1")
port = int(os.environ.get("CANENGINE_PORT", "8080"))
```

打包器将发布manifest的`runtime.web.executable`改为`backend/<outputName>`，移除脚本参数、PythonAdapter/PythonPath和Python运行时需求；保留其余CLI参数、Web权限、readyPath、网络及数据目录声明。Python脚本入口会替换为原生程序入口；已有HTML入口必须在assets中提供。源码manifest不被改写。资源从APP_DIR读取，数据写入APP_DATA_DIR，不写回包内。

## 开发环境与打包

在CanEngine“我的→CEAPP打包与签名”拖入**一个源码项目根目录**，点击“开始打包并签名”。Canvas的CEAPP打包入口复用同一浮层：默认普通打包，选择“源码保护打包（高级）”后才检查/安装编译环境，显示实际本机目标并确认打包。两种模式都在该浮层内启用导入密码，My主页面不再单独设置。环境就绪状态用绿色，按钮文案为“安装编译环境”。执行期间浮层保持打开，显示真实构建阶段、折叠日志及取消；完成后可复制路径、打开所在位置或进入安装预览。重复提交被拒绝；失败或取消不覆盖已存在的发布包，也不自动退回源码包。

- 完整Python3及Python.h、对应CPU架构；精简运行时不足以编译。
- Mac：Apple Command Line Tools/Clang。Windows amd64：MSVC C++ Build Tools及Windows SDK。
- Nuitka4.2.2及其Python依赖在用户专属开发工具缓存中按需准备。完整Python与系统C编译工具由开发者先安装；普通用户运行已编译CEAPP无需这些开发工具。
- Windows首次准备会实编译一个标准库小程序，下载并缓存Nuitka所需的原生DLL依赖扫描工具。完成后才标记环境就绪，正式打包不会要求在命令行回答下载提示。
- 项目第三方Python依赖需预先安装在构建Python环境中；不会继承开发机任意site-packages、API Key或自动执行项目安装脚本。CLI可用`-build-python`指定已准备Nuitka及依赖的完整Python。原生库许可及目标OS兼容性仍需项目自行确认。

源码宿主CLI：

```bash
go run ./cmd/ceapp-build -check
go run ./cmd/ceapp-build -prepare
go run ./cmd/ceapp-build -src /path/to/source -out /path/to/new-release
```

`ceapp-build`显式生成原生发布目录，`-out`必须是新目录，缺少配置会失败。`ceapp-pack -src <source>`默认普通打包；`ceapp-pack -mode python -src <source>`才读取配置并编译保护，`-build-python`必须与`-mode python`一起使用。版本覆盖参数仅在用户明确要求时使用。不得制造官方/KOL身份或把签名私钥放进项目。

Nuitka的“commercial grade 'not installed'”表示付费扩展未安装，不影响标准版编译。此行及明确的anti-bloat提示作为普通日志；真实ImportError/ModuleNotFoundError和编译失败必须保留并停止保护构建。打包在替换目标前校验完整性及Ed25519签名。

## 解包后的文件与验收

```text
<installed-app>/
  app.json
  ceapp.native.json            # 构建记录
  backend/
    canwechat-server          # Windows为canwechat-server.exe
    <本平台运行依赖/动态库>
  frontend/                   # 原有HTML、JS、CSS
  assets/
  vendor/                     # 仅明确选入且适配平台的资源
```

业务.py、.pyc、构建配置、临时C源码和编译报告不进入发布包；源码和开发工具缓存分别保留。编译增加的是对应CEAPP后端及依赖大小，主客户端没有内置Python编译器/MSVC/Xcode。前端和静态资源仍可读，二进制仍可逆向，不能承诺绝对源码保密。

结构校验只能证明配置形状。每个平台还须验证实际编译、二进制架构、解包无业务源码、签名/安装、健康检查、前端、数据持久化、外部目录权限、核心业务及缺失开发工具/取消路径。macOS成功不等于Windows原生验收。记录实际编译出的最低OS要求，不能从宿主最低版本推定后端兼容旧OS。

## 多平台合成一个CEAPP

在每个目标OS/CPU上构建同一份源码。通过共享浮层“导出本平台产物”或`ceapp-build -src <source> -out <local>.cebuild`生成本机产物。在最终打包机器选择“源码保护打包（高级）”，保留本机目标，勾选已声明的其他平台并导入对应`.cebuild`，然后统一打包与签名。不能在Mac上直接编译Windows；Mac Intel与Apple Silicon也需要匹配产物。未声明的平台不可勾选，缺少产物时不能开始打包。

CLI合包：`ceapp-pack -mode python -src <source> -targets darwin/arm64,windows/amd64 -artifact <windows>.cebuild -out <final>.ceapp`，签名参数按既有流程提供。`-artifact`可重复，额外平台每项恰好一个，本机在最终打包时重新编译。`ceapp-build`也可输出新的多平台发布目录，但`.cebuild`导出只接受本机单平台。

`.cebuild`是开发者交换ZIP，包含原生后端、白名单资源、发布manifest和`ceapp.native.json`。它未签名、不能直接安装，不应把整个产物放入应用assets。导入不运行它；核对appId/版本/OS/CPU、源码指纹、Web运行契约、文件SHA256和二进制头，合并再核对公共资源完全一致。指纹不提供构建来源证明，请从可信构建环境接收产物。最终签名覆盖所有平台文件。源代码或公共资源变化后必须重新导出各个平台。

最终布局为公共资源一次加各平台backend：`backend/darwin-arm64/<name>`、`backend/darwin-amd64/<name>`、`backend/windows-amd64/<name>.exe`。manifest使用：

```json
{
  "platforms": [{"os":"darwin","arch":"arm64"},{"os":"windows","arch":"amd64"}],
  "runtime": {"web": {
    "nativeTargets": [
      {"os":"darwin","arch":"arm64","executable":"backend/darwin-arm64/server"},
      {"os":"windows","arch":"amd64","executable":"backend/windows-amd64/server.exe"}
    ],
    "readyPath":"/health", "network":"loopback"
  }}
}
```

这是发布manifest局部示例，源码项目仍用Python启动配置。nativeTargets和platforms必须逐项匹配，禁止默认executable、PythonAdapter/PythonPath、额外运行时和commands；公共参数仍保留。Python脚本entry在合包后用ceapp.native.json作容器锚点，真正启动入口由nativeTargets选择。宿主先验证整个签名容器，再仅解出本机backend及公共资源，运行时再次选择精确OS/CPU。不支持的平台拒绝，不回退到别的平台或源码。

需要包含此实现的1.8.0构建，版本号不变。业务跨平台依赖仍需迁移；CanWeChat目前仍是Mac arm64。结构夹具和Windows宿主交叉构建不等于Windows原生编译或安装/运行成功。
