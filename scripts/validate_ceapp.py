#!/usr/bin/env python3
"""Structural release gate. PASS is not native-host or semantic runtime verification."""
import argparse
import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from web_manifest import validate_web
from build_manifest import validate_build
from browser_prefill import PROFILE, validate_browser, validate_request

class References(HTMLParser):
    def __init__(self):super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('script','img','audio','video','source') and attrs.get('src'):self.paths.append(attrs['src'])
        if tag=='link' and attrs.get('href'):self.paths.append(attrs['href'])

def validate(root: Path):
    root=root.resolve();errors=[];warnings=[];checks=[]
    def require(condition,message):
        if not condition: errors.append(message)
    def local(path):
        p=Path(str(path))
        if not str(path) or p.is_absolute() or '..' in p.parts or '\\' in str(path) or ':' in str(path):
            errors.append('Unsafe or remote package path: '+str(path));return False
        actual=root/p
        if not actual.resolve().is_relative_to(root) or actual.is_symlink():
            errors.append('Path escapes package root: '+str(path));return False
        if not actual.is_file():errors.append('Missing package file: '+str(path));return False
        return True
    try:
        manifest=json.loads((root/'app.json').read_text(encoding='utf-8'))
        runtime=manifest.get('runtime') or {}
        remote=runtime.get('remoteWeb') is not None
        web=runtime.get('web') is not None
        config={}
        if not (remote or web):
            config_text=(root/'app-config.js').read_text(encoding='utf-8')
            config=json.loads(config_text.split('=',1)[1].strip().removesuffix(';'))
    except (OSError,ValueError,IndexError) as exc:return {'ok':False,'errors':['Manifest/config: '+str(exc)],'warnings':[],'checks':[]}
    require(manifest.get('schemaVersion')==1,'schemaVersion must be 1')
    require(bool(re.fullmatch(r'[a-z0-9][a-z0-9-]*',manifest.get('appId',''))),'Invalid appId')
    if not (remote or web): require(config.get('appId')==manifest.get('appId'),'appId mismatch between manifest and code')
    errors.extend(validate_web(manifest,root))
    errors.extend(validate_browser(manifest))
    build_path = root/'ceapp.build.json'
    if build_path.exists():
        try:
            require(build_path.is_file() and not build_path.is_symlink() and build_path.stat().st_size <= 64*1024, 'Build configuration must be a regular JSON file up to 64 KiB')
            if build_path.is_file() and build_path.stat().st_size <= 64*1024:
                errors.extend(validate_build(json.loads(build_path.read_text(encoding='utf-8')),manifest,root))
                checks.append('python-build-config')
                warnings.append('Authoring source is not a compiled release. Build and verify native output on each declared OS/architecture; app/host versions must be preserved.')
        except (OSError,ValueError) as exc:
            errors.append('Build configuration: '+str(exc))
    if remote or web: checks.append('web-manifest-structure')
    require(bool(re.fullmatch(r'\d+\.\d+\.\d+',manifest.get('version',''))),'App version must be x.y.z')
    permissions=manifest.get('permissions')
    require(isinstance(permissions,list) and all(isinstance(p,str) for p in permissions),'permissions must be flat string[]')
    permissions=permissions if isinstance(permissions,list) else []
    allowed={'ai.text.generate','ai.vision.analyze','ai.image.generate','ai.video.generate','ai.model3d.generate',
             'notification.send','notification.schedule','data.read','data.write','data.action','data.schema',
             'web.network','web.files.read','web.files.write','canvas.wechat.import',
             'browser.form.prefill','browser.mdac.fill',
             *('phoneBridge.'+s for s in ('openPanel','createSession','receiveFiles','readFiles','addFiles','sendToPhone'))}
    require(set(permissions)<=allowed,'Permission outside verified baseline; update contract/validator from source before using it')
    require(len(set(permissions))==len(permissions),'Duplicate permissions')
    caps=manifest.get('capabilities') or {}
    browser=caps.get('browser') or {}
    if not isinstance(browser,dict): browser={}
    if browser:
        checks.append('controlled-browser-manifest')
    form_config=root/'assets/form-config.json'
    if form_config.exists():
        try:
            require(form_config.is_file() and not form_config.is_symlink() and form_config.stat().st_size <= 128*1024, 'Form configuration must be a regular bounded JSON file')
            if form_config.is_file() and form_config.stat().st_size <= 128*1024:
                form=json.loads(form_config.read_text(encoding='utf-8'))
                if not isinstance(form,dict): raise ValueError('Invalid form configuration')
                require(isinstance(form,dict) and form.get('schemaVersion')==1, 'Form configuration schemaVersion must be 1')
                targets={t['id'] for t in browser.get('targets',[]) if isinstance(t,dict) and isinstance(t.get('id'),str)}
                require(PROFILE in browser.get('profiles',[]), 'Form configuration requires form-prefill-v1')
                errors.extend(validate_request(form.get('request'),targets))
                checks.append('prefill-request-structure')
        except (OSError,ValueError,TypeError,UnicodeError):
            errors.append('Form configuration is invalid; inspect the local file without logging field values')
    features=caps.get('ai',{}).get('features',[])
    require(set(features)<=set(permissions),'AI feature missing corresponding permission')
    require('ai.video.create' not in permissions,'video method is create; permission is ai.video.generate')
    data=caps.get('dataBridge',{})
    require(config.get('datasets',[])==data.get('datasets',[]),'Configured dataset IDs differ from manifest')
    require(config.get('actions',[])==data.get('actions',[]),'Configured action IDs differ from manifest')
    for kind in ('datasets','actions'):
        require(all(isinstance(x,str) and x and '*' not in x for x in data.get(kind,[])),'Exact '+kind+' IDs required')
    local_schema=data.get('local',{})
    if local_schema.get('enabled'):
        require({'data.read','data.write'}<=set(permissions),'Local demo needs data.read and data.write')
        path=local_schema.get('schemaEntry','')
        if local(path):
            try: schema=json.loads((root/path).read_text());require('bridge_lab_notes' in schema.get('collections',[]),'Local demo collection missing from schema')
            except (OSError,ValueError) as e:errors.append('Invalid local schema: '+str(e))
    cmds=manifest.get('commands',{})
    if cmds is None and (remote or web): cmds={}
    require(isinstance(cmds,dict) and (bool(cmds) or remote or web),'Static apps need commands; Web apps allow empty commands')
    if isinstance(cmds,dict) and not (remote or web):
        for cid,spec in cmds.items():
            executable=spec.get('executable','')
            require(executable in ('python3','echo'),'Unknown demo executable: '+executable)
            require(isinstance(spec.get('baseArgs'),list),'baseArgs must be an array: '+cid)
            if executable=='python3':
                base=spec.get('baseArgs',[])
                require(bool(base),'Python entry missing')
                if base: local(base[0])
                flags=spec.get('allowedFlags',[])
                require(flags==['--sleep'],'Demo allowedFlags must match process_file.py')
                require(any(r.get('id')=='python-runtime' for r in manifest.get('runtime',{}).get('requirements',[])),'Python runtime requirement missing')
    if not remote: local(manifest.get('entry',''))
    if manifest.get('icon'): local(manifest['icon'])
    for key in ('nameI18n','descriptionI18n'):require({'zh-CN','en-US'}<=set(manifest.get(key,{})),'Missing bilingual metadata: '+key)
    for file in root.rglob('*'):
        if not file.is_file():continue
        rel=file.relative_to(root).as_posix()
        require(not file.is_symlink(),'Symlink not allowed: '+rel)
        require(not any(part in ('node_modules','__pycache__','.git','backups','tests') for part in file.parts),'Development artifact in app: '+rel)
        require(file.name!='.DS_Store' and file.suffix not in ('.pyc','.zip','.ceapp','.cebuild','.pem','.key','.sqlite'),'Excluded artifact: '+rel)
        if remote:
            require(file.suffix.lower() not in ('.php','.phtml') and file.name != '.env' and not file.name.startswith('.env.'), 'Remote CEAPP must not contain website PHP or server configuration: '+rel)
        if file.suffix in ('.js','.css','.html','.py'):
            text=file.read_text(encoding='utf-8')
            require(not re.search(r'(?:https?:)?//(?:cdn\.|unpkg\.|fonts\.google)',text),'Remote startup dependency: '+rel)
            require(not re.search(r'window\.(?:runtime|go)\b|child_process|eval\s*\(',text),'Forbidden host bypass or eval: '+rel)
            require(not re.search(r'\b(?:sk-[A-Za-z0-9]{20,}|BEGIN .*PRIVATE KEY)\b',text),'Possible secret: '+rel)
        if file.suffix=='.html':
            refs=References();refs.feed(file.read_text(encoding='utf-8'))
            for path in refs.paths:
                if path.startswith('data:'):continue
                local(path.lstrip('/') if web and path.startswith('/') else (file.parent.relative_to(root)/path).as_posix())
        if file.suffix=='.css':
            for path in re.findall(r'url\([\'\"]?([^\)\'\"]+)',file.read_text()):
                if not path.startswith('data:'):local((file.parent.relative_to(root)/path).as_posix())
        if file.suffix=='.py':
            try:ast.parse(file.read_text(encoding='utf-8'));checks.append('python-syntax:'+rel)
            except SyntaxError as e:errors.append(str(e))
        if file.suffix=='.js':
            node=shutil.which('node')
            if not node:errors.append('Node required for JS syntax gate');continue
            result=subprocess.run([node,'--check',str(file)],capture_output=True,text=True,timeout=15)
            if result.returncode:errors.append('JS syntax '+rel+': '+result.stderr[:600])
            else:checks.append('js-syntax:'+rel)
    sections=config.get('sections',[])
    if 'jobs' in sections:require('inspect' in cmds,'Jobs panel without inspect command')
    if 'ai' in sections:require('ai.text.generate' in features,'AI panel missing text feature')
    if config.get('media'):require({'ai.vision.analyze','ai.image.generate','ai.video.generate','ai.model3d.generate'}<=set(features),'Media UI missing manifest features')
    if 'phone' in sections:require(all('phoneBridge.'+p in permissions for p in ('openPanel','createSession','receiveFiles','readFiles','addFiles','sendToPhone')),'Phone panel missing permission')
    if config.get('notifications'):require('notification.send' in permissions,'Notification button missing permission')
    if data.get('datasets'):require('data.schema' in permissions,'Dataset demo schema permission missing')
    if data.get('actions'):require('data.action' in permissions,'Data action permission missing')
    if remote: warnings.append('Online website content, storage, login, upload/download and popup behavior require native acceptance; no Host Bridge is injected.')
    if remote and isinstance(runtime['remoteWeb'],dict) and runtime['remoteWeb'].get('authorization') == 'canengine':
        checks.append('remote-web-authorization-manifest')
        warnings.append('Protection also requires matching app registration, server-side ticket verification and a CanEngine 1.8.0 build containing this feature. Source validation does not prove a successful handshake or protected website access.')
    if web: warnings.append('Web setup mappings, sandbox availability and runtime behavior must also pass the authoritative CanEngine manifest and native gates.')
    if browser: warnings.append('Prefill schema checks do not inspect CSS uniqueness, protected controls, site events or native compatibility. Research the actual website and test synthetic data in installed CanEngine; do not submit.')
    warnings.append('Native host/WebView/real AI/phone/signing acceptance is a separate mandatory gate.')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'checks':checks,'appId':manifest.get('appId'),'runtimeMode':'remote-web' if remote else 'web' if web else 'static'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('--report',type=Path);args=parser.parse_args()
    try: report=validate(args.root)
    except Exception as exc: report={'ok':False,'errors':['Validator failed: '+str(exc)]}
    text=json.dumps(report,ensure_ascii=False,indent=2);print(text)
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text+'\n',encoding='utf-8')
    sys.exit(0 if report['ok'] else 1)
