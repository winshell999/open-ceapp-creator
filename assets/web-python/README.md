# 常驻本地Web示例

最低CanEngine 1.8.0。本地Python HTTP后端保留路由、内存状态和SQLite连接；只有应用关闭才结束进程。前端资产及中英文文案随包提供。

将这个单独目录交给CanEngine签名器，安装后测试重复读取、保存笔记、关闭重开、原生下载和语言。包内entry为server.py，commands可以为空；写入使用CANENGINE_APP_DATA_DIR，运行时和沙箱由宿主检查。

普通浏览器预览可运行python3 server.py（开发模式的数据写入.local-data，打包前移走）。这不验证Host Bridge、原生下载或隔离环境。第三方项目迁移参见创建Skill的references/local-web-runtime-1.8.0.md。

需要编译发布时，用创建器的web-python --compile-python选项生成ceapp.build.json。此后在匹配的1.8.0宿主准备编译环境，分别在Mac/Windows目标机器编译、打包和签名。模板同时读取CANENGINE_HOST/PORT、APP_DIR和APP_DATA_DIR，兼容源码及原生后端。未选择编译时保持普通Python运行方式。详细规则见references/python-compiled-packaging.md。
