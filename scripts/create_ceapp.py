#!/usr/bin/env python3
"""Generate a self-contained CEAPP source project with least-privilege profiles."""
import argparse
import json
from pathlib import Path
import re
import shutil
from web_manifest import origin, validate_web
from browser_prefill import read_request, target_url, validate_browser, validate_request

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {
    'minimal': ['overview', 'system', 'diagnostics'],
    'files': ['overview', 'files', 'system', 'diagnostics'],
    'python': ['overview', 'files', 'jobs', 'runtime', 'system', 'diagnostics'],
    'ai-text': ['overview', 'ai', 'system', 'diagnostics'],
    'ai-media': ['overview', 'files', 'ai', 'system', 'diagnostics'],
    'data': ['overview', 'data', 'system', 'diagnostics'],
    'phone': ['overview', 'files', 'phone', 'system', 'diagnostics'],
    'notifications': ['overview', 'system', 'diagnostics'],
    'full': ['overview', 'files', 'jobs', 'runtime', 'ai', 'data', 'phone', 'system', 'diagnostics'],
    'web-python': [],
    'remote-web': [],
    'form-prefill': []
}

def settings(app_id: str, name: str, profile: str, datasets=(), actions=()):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', app_id):
        raise ValueError('app-id must contain only lowercase letters, digits and hyphens')
    if profile not in PROFILES:
        raise ValueError('Unknown profile')
    if (datasets or actions) and 'data' not in PROFILES[profile]:
        raise ValueError('Shared datasets/actions require the data or full profile')
    if any(not x or '*' in x for x in [*datasets, *actions]):
        raise ValueError('Use exact dataset/action identifiers, no wildcards')
    sections = PROFILES[profile]
    config = {'appId': app_id, 'profile': profile, 'sections': sections,
              'media': profile in ('ai-media','full'),
              'notifications': profile in ('notifications','full'),
              'datasets': list(datasets), 'actions': list(actions)}
    manifest = {
        'schemaVersion': 1, 'appId': app_id, 'name': name,
        'nameI18n': {'zh-CN': name, 'en-US': name}, 'version': '1.8.0',
        'description': 'CanEngine public bridge demonstration: ' + profile,
        'descriptionI18n': {'zh-CN': 'CanEngine \u6865\u63a5\u6f14\u793a', 'en-US':'CanEngine public bridge demonstration'},
        'entry':'index.html', 'icon':'assets/logo.png', 'minCanEngineVersion':'1.8.0',
        'platforms':[{'os':'*','arch':'*'}],
        'runtime':{'requirements':[{'id':'base-runtime','optional':True}]},
        'commands':{'noop':{'executable':'echo','baseArgs':[app_id]}},
        'capabilities':{}, 'permissions':[]
    }
    if 'jobs' in sections:
        manifest['runtime']['requirements'].append({'id':'python-runtime','optional':True})
        manifest['commands']={'inspect':{'executable':'python3','baseArgs':['scripts/process_file.py'],'allowedFlags':['--sleep']}}
    caps,permissions=manifest['capabilities'],manifest['permissions']
    if 'ai' in sections:
        features=['ai.text.generate']
        if config['media']:
            features += ['ai.vision.analyze','ai.image.generate','ai.model3d.generate','ai.video.generate']
        caps['ai']={'required':False,'features':features};permissions.extend(features)
    if 'data' in sections:
        caps['dataBridge']={'required':False,'datasets':list(datasets),'actions':list(actions),'mode':'read',
                           'local':{'enabled':True,'dbFile':'bridge-lab.sqlite','schemaEntry':'data/localdb.schema.json','schemaVersion':1}}
        permissions.extend(['data.read','data.write'])
        if datasets: permissions.append('data.schema')
        if actions: permissions.append('data.action')
    if 'phone' in sections:
        permissions.extend('phoneBridge.'+x for x in ['openPanel','createSession','receiveFiles','readFiles','addFiles','sendToPhone'])
    if config['notifications']:
        caps['notification']={'required':False,'reason':'User-triggered test notification','capabilities':['send']}
        permissions.append('notification.send')
    return manifest, config

def generate(output: Path, app_id: str, name: str, profile: str, datasets=(), actions=(), url=None, allowed_origins=(), storage='persistent', compile_python=False, mapping=None, authorization=''):
    manifest, config = settings(app_id,name,profile,datasets,actions)
    if authorization not in ('', 'canengine'):
        raise ValueError('Remote authorization supports only canengine')
    if authorization and profile != 'remote-web':
        raise ValueError('--authorization requires the remote-web profile')
    if compile_python and profile != 'web-python':
        raise ValueError('--compile-python currently requires the web-python profile (runtime.web with empty commands)')
    if mapping is not None and profile != 'form-prefill':
        raise ValueError('--mapping is supported only for form-prefill')
    output=output.resolve()
    if output.exists():
        raise ValueError('Destination already exists; use a new directory to protect existing work')
    if profile == 'form-prefill':
        target_url(url)
        if mapping is None:
            raise ValueError('form-prefill requires --mapping with a researched JSON request using synthetic values')
        if allowed_origins:
            raise ValueError('Prefill uses fixed manifest targets, not --allowed-origin')
        request = read_request(Path(mapping)) if not isinstance(mapping, dict) else mapping
        issues = validate_request(request)
        if issues:
            raise ValueError('; '.join(issues))
        template = ROOT/'assets'/'form-prefill'
        prefill_manifest = json.loads((template/'app.json').read_text(encoding='utf-8'))
        prefill_manifest.update(appId=app_id, name=name, nameI18n={'zh-CN':name, 'en-US':name})
        prefill_manifest['capabilities']['browser']['targets'] = [{'id':request['target'], 'url':url}]
        issues = validate_browser(prefill_manifest)
        if issues:
            raise ValueError('; '.join(issues))
        shutil.copytree(template, output, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        (output/'app.json').write_text(json.dumps(prefill_manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        config = {'schemaVersion':1, 'request':request, 'titleI18n':prefill_manifest['nameI18n'], 'labels':{}, 'options':{}, 'formatHints':{}}
        (output/'assets/form-config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        return output
    if profile in ('web-python','remote-web'):
        template = ROOT/'assets'/profile
        web_manifest = json.loads((template/'app.json').read_text(encoding='utf-8'))
        web_manifest.update(appId=app_id, name=name, nameI18n={'zh-CN':name,'en-US':name})
        if profile == 'remote-web':
            origin(url)
            for raw in allowed_origins: origin(raw, exact=True)
            web_manifest['runtime']['remoteWeb'] = {'url':url,'storage':storage}
            if authorization: web_manifest['runtime']['remoteWeb']['authorization'] = authorization
            if allowed_origins: web_manifest['runtime']['remoteWeb']['allowedOrigins'] = list(allowed_origins)
            web_manifest['description'] = 'Online website managed by CanEngine.'
            web_manifest['descriptionI18n'] = {'zh-CN':'通过CanEngine访问的网站应用，需要网络。','en-US':'A website managed by CanEngine. Requires internet access.'}
            issues = validate_web(web_manifest, output)
            if issues: raise ValueError('; '.join(issues))
        shutil.copytree(template,output,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store','.local-data'))
        (output/'app.json').write_text(json.dumps(web_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if compile_python:
            build_config = {
                'schemaVersion': 1,
                'python': {'entry':'server.py', 'outputName':'web-server'},
                'assets': ['index.html', 'assets'],
                'targets': [{'os':'darwin','arch':'arm64'}, {'os':'darwin','arch':'amd64'}, {'os':'windows','arch':'amd64'}]
            }
            (output/'ceapp.build.json').write_text(json.dumps(build_config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            with (output/'README.md').open('a',encoding='utf-8') as readme:
                readme.write('\n## 可选编译保护\n\n项目含ceapp.build.json。使用包含Python编译功能的CanEngine 1.8.0构建，点击“开始打包并签名”，在“我的”和画布共用浮层中明确选择“Python编译保护”，再检查/准备编译环境、编译、打包和签名。默认“普通打包”保留源码与平台声明，不需要编译工具；兼容Mac/Windows的源码应用可使用一个CEAPP包。Mac和Windows编译保护使用同一配置，必须在对应系统和架构分别构建；编译输出包只声明实际构建平台。编译工具按需下载，不随普通CanEngine安装包提供。编译失败会停止，不会自动退回源码包。CLI保护打包须传-mode python。\n\n编译发布包包含app.json、backend原生程序及运行依赖、index.html和assets。server.py和构建配置保留在源码项目中，不进入编译发布包；已有版本号保持不变。前端仍然可读，编译不能保证不可逆向。两种打包方式都可启用导入密码，并在写出前校验完整性和签名。\n')
        if profile == 'remote-web':
            (output/'README.md').write_text('# '+name+'\n\nRemote website source. Requires a CanEngine 1.8.0 build with native right-pane embedding, macOS 14+ or Windows amd64 with WebView2.\n\nEntry: '+url+'\n\nThe website opens directly in the host main window\'s right pane, with the left navigation intact and no separate window or navigation toolbar. Switching apps preserves the page; host dialogs temporarily hide it. Reload/browser/cache/data actions are in the running app entry\'s context menu. No extra embedding flag, local HTML, commands or Host Bridge. Storage: '+storage+'. Ephemeral data is discarded when the app closes.\n\nSign and install through CanEngine. Website caches obey HTTP policy and do not guarantee offline startup or business-data persistence. Different test/production appIds keep storage separate. Cross-origin login needs exact allowedOrigins and native acceptance. New-window links currently navigate in the same website view.\n',encoding='utf-8')
            if authorization:
                with (output/'README.md').open('a',encoding='utf-8') as readme:
                    readme.write('\nCanEngine authorization is enabled. Use a matching 1.8.0 build containing the remote website license handshake. Register this exact appId and entry URL with the license center and protect the website on its server. A valid formal CanEngine license covers all registered protected apps; trials are denied. Each new open requests a fresh one-time ticket; switching views and ordinary refresh reuse the fixed website session (at most eight hours and never beyond license expiry). Website keys, License Tokens, tickets and PHP/backend files belong outside this CEAPP source and package. A manifest declaration alone does not protect direct browser access.\n')
        return output
    shutil.copytree(ROOT/'assets'/'starter', output, ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store','*.sqlite'))
    configure(output,manifest,config)
    return output

def configure(output: Path, manifest: dict, config: dict):
    (output/'app.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'app-config.js').write_text('window.CEAPP_CONFIG = '+json.dumps(config,ensure_ascii=True,indent=2)+';\n',encoding='utf-8')
    if 'jobs' not in config['sections']: shutil.rmtree(output/'scripts',ignore_errors=True)
    if 'data' not in config['sections']: shutil.rmtree(output/'data',ignore_errors=True)
    (output/'README.md').write_text(
        '# '+manifest['name']+'\n\n'
        'Profile: `'+config['profile']+'`. This is CEAPP SOURCE, not a signed .ceapp.\n\n'
        '1. Open index.html for the browser-only UI and local file preview.\n'
        '2. Drag this directory into CanEngine packaging/signing, install and open it.\n'
        '3. On Overview, inspect host identity. Use feature buttons individually.\n'
        '4. For Python: Files > Sample file, Python tasks > Inspect file, then export.\n'
        '5. AI, notifications and phone send occur only after explicit clicks/confirmation.\n'
        '6. Local database: save/read/list/delete the fixed demo note. Shared IDs must be configured.\n\n'
        'Browser appearance and simulated tests do not prove native host acceptance.\n'
        'No user API keys, signing keys or provider URLs belong in this source.\n'
        'The app shell is local; AI/network/phone features are not guaranteed offline.\n'
        'The no-op command in UI-only profiles satisfies the packer and is never executed.\n',encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--app-id',required=True)
    parser.add_argument('--name',default='CEAPP Bridge Lab')
    parser.add_argument('--profile',choices=list(PROFILES),default='minimal')
    parser.add_argument('--dataset',action='append',default=[])
    parser.add_argument('--action',action='append',default=[])
    parser.add_argument('--url',help='Website entry for remote-web; fixed HTTPS page for form-prefill')
    parser.add_argument('--mapping',type=Path,help='Researched prefill request JSON with synthetic fixture values; required for form-prefill')
    parser.add_argument('--allowed-origin',action='append',default=[],help='Additional exact top-level navigation origin')
    parser.add_argument('--storage',choices=['persistent','ephemeral'],default='persistent')
    parser.add_argument('--authorization',choices=['canengine'],default='',help='Require CanEngine formal-license handshake; remote-web only, website server verification required')
    parser.add_argument('--compile-python',action='store_true',help='Add automatic native Python packaging configuration; web-python only')
    args=parser.parse_args()
    try: print(generate(args.output,args.app_id,args.name,args.profile,args.dataset,args.action,args.url,args.allowed_origin,args.storage,args.compile_python,args.mapping,authorization=args.authorization))
    except (OSError,ValueError) as exc: parser.exit(1,str(exc)+'\n')
