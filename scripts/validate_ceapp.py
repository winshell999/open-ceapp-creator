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
        config_text=(root/'app-config.js').read_text(encoding='utf-8')
        config=json.loads(config_text.split('=',1)[1].strip().removesuffix(';'))
    except (OSError,ValueError,IndexError) as exc:return {'ok':False,'errors':['Manifest/config: '+str(exc)],'warnings':[],'checks':[]}
    require(manifest.get('schemaVersion')==1,'schemaVersion must be 1')
    require(bool(re.fullmatch(r'[a-z0-9][a-z0-9-]*',manifest.get('appId',''))),'Invalid appId')
    require(config.get('appId')==manifest.get('appId'),'appId mismatch between manifest and code')
    require(bool(re.fullmatch(r'\d+\.\d+\.\d+',manifest.get('version',''))),'App version must be x.y.z')
    permissions=manifest.get('permissions')
    require(isinstance(permissions,list) and all(isinstance(p,str) for p in permissions),'permissions must be flat string[]')
    permissions=permissions if isinstance(permissions,list) else []
    allowed={'ai.text.generate','ai.vision.analyze','ai.image.generate','ai.video.generate','ai.model3d.generate',
             'notification.send','notification.schedule','data.read','data.write','data.action','data.schema',
             *('phoneBridge.'+s for s in ('openPanel','createSession','receiveFiles','readFiles','addFiles','sendToPhone'))}
    require(set(permissions)<=allowed,'Permission outside verified baseline; update contract/validator from source before using it')
    require(len(set(permissions))==len(permissions),'Duplicate permissions')
    caps=manifest.get('capabilities',{})
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
    require(isinstance(cmds,dict) and bool(cmds),'commands cannot be empty for the current packer')
    if isinstance(cmds,dict):
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
    for key in ('entry','icon'):local(manifest.get(key,''))
    for key in ('nameI18n','descriptionI18n'):require({'zh-CN','en-US'}<=set(manifest.get(key,{})),'Missing bilingual metadata: '+key)
    for file in root.rglob('*'):
        if not file.is_file():continue
        rel=file.relative_to(root).as_posix()
        require(not file.is_symlink(),'Symlink not allowed: '+rel)
        require(not any(part in ('node_modules','__pycache__','.git','backups','tests') for part in file.parts),'Development artifact in app: '+rel)
        require(file.name!='.DS_Store' and file.suffix not in ('.pyc','.zip','.ceapp','.pem','.key','.sqlite'),'Excluded artifact: '+rel)
        if file.suffix in ('.js','.css','.html','.py'):
            text=file.read_text(encoding='utf-8')
            require(not re.search(r'(?:https?:)?//(?:cdn\.|unpkg\.|fonts\.google)',text),'Remote startup dependency: '+rel)
            require(not re.search(r'window\.(?:runtime|go)\b|child_process|eval\s*\(',text),'Forbidden host bypass or eval: '+rel)
            require(not re.search(r'\b(?:sk-[A-Za-z0-9]{20,}|BEGIN .*PRIVATE KEY)\b',text),'Possible secret: '+rel)
        if file.suffix=='.html':
            refs=References();refs.feed(file.read_text(encoding='utf-8'))
            for path in refs.paths:
                if path.startswith('data:'):continue
                local((file.parent.relative_to(root)/path).as_posix())
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
    warnings.append('Native host/WebView/real AI/phone/signing acceptance is a separate mandatory gate.')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'checks':checks,'appId':manifest.get('appId')}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('--report',type=Path);args=parser.parse_args()
    try: report=validate(args.root)
    except Exception as exc: report={'ok':False,'errors':['Validator failed: '+str(exc)]}
    text=json.dumps(report,ensure_ascii=False,indent=2);print(text)
    if args.report:args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(text+'\n',encoding='utf-8')
    sys.exit(0 if report['ok'] else 1)
