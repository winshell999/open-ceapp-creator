#!/usr/bin/env python3
"""Real Chromium UI checks with no host, then explicitly simulated host fixtures.
Run with --app path/to/ceapp --out path/to/report. No server is started.
"""
import argparse
import json
import mimetypes
import shutil
import re
import base64
from urllib.parse import urlparse, unquote
from pathlib import Path
from playwright.sync_api import sync_playwright

FAKE_HOST=r"""
window.__fixtureCalls=[];
const calls=window.__fixtureCalls;
const ok=(name,value)=>(...args)=>{calls.push({name,args});return Promise.resolve(value);};
const files=[{id:'fixture-file',name:'sample.csv',path:'/fixture/sample.csv',size:30,mime:'text/csv'}];
let stored={};const listeners={};
window.CanEngine={
 getLocale:()=> 'zh-CN',setLocale:ok('locale','zh-CN'),onLocaleChange:()=>()=>{},
 getHostVersion:ok('version',{hostVersion:'fixture-only',apiVersion:'test',platform:'simulated'}),
 getCapabilities:ok('caps',{capabilities:[]}),onFileDrop:()=>()=>{},
 chooseFile:ok('choose',files[0]),chooseFiles:ok('chooseMany',files),chooseDirectory:ok('dir',{id:'dir',writable:true}),stageFile:ok('stage',files[0]),removeStagedFile:ok('remove',{ok:true}),
 openExternalURL:ok('web',null),openFile:ok('open',{ok:true}),revealFile:ok('reveal',{ok:true}),exportFile:ok('export',{name:'saved'}),
 requireRuntime:ok('runtime',{ok:true}),getRuntimeStatus:ok('runtimes',{ok:true,runtimes:[]}),getAppRuntimeStatus:ok('appRuntime',{}),installRuntime:ok('install',{ok:true}),
 onEvent:(name,fn)=>{listeners[name]=fn;return()=>delete listeners[name];},listJobs:ok('listJobs',[]),
 runJob:async request=>{calls.push({name:'runJob',args:[request]});const job={id:'fixture-job',appId:request.appId,commandId:'inspect',status:'success',ok:true,files:[{fileRef:'fixture-ref',name:'inspection.json',path:'/fixture/out',size:30}]};return job;},getJob:ok('getJob',{}),getJobLogs:ok('logs',{}),cancelJob:ok('cancelJob',null),
 ai:{getStatus:ok('aiStatus',{}),text:{generate:ok('aiText',{text:'SIMULATED AI RESPONSE'})},vision:{analyze:ok('vision',{text:'SIMULATED VISION'})},image:{generate:ok('image',{images:[]})},video:{create:ok('video',{taskId:'fixture-task',status:'success'}),getTask:ok('videoTask',{status:'success'}),cancelTask:ok('cancelTask',null)},model3d:{generate:ok('model3d',{taskId:'fixture-3d',status:'success'}),getTask:ok('3dTask',{status:'success'}),cancelTask:ok('cancel3d',null)}},
 data:{local:()=>({put:async r=>{stored=r;return r;},get:async()=>stored,find:async()=>({rows:stored.id?[stored]:[]}),delete:async()=>{stored={};return{ok:true};}})},
 phoneBridge:{openPanel:ok('phonePanel',true),createSession:ok('phoneSession',{sessionId:'redacted'}),onFilesReceived:()=>()=>{},readFile:async()=>new Blob(['sample'],{type:'text/plain'}),addFile:ok('phoneAdd',{fileId:'fixture-phone'}),sendToPhone:ok('phoneSend',{ok:true})},
 notification:{send:ok('notify',{ok:true}),getStatus:ok('notifyStatus',{}),openSettings:ok('notifySettings',null)},
 clipboard:{writeText:ok('clipboard',true)},printHTML:ok('print',null),getDiagnostics:ok('diag',{apiKey:'secret-test'}),exportDiagnostics:ok('exportDiag',{name:'diag.json'}),
 assetURL:async()=>window.__fixtureAsset
};
"""

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--app',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--browser');args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 checks=[];errors=[];external=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=args.browser or shutil.which('chromium') or p.chromium.executable_path,headless=True,args=['--no-sandbox'])
  def load(page, fixture=False):
   html=(args.app/'index.html').read_text(encoding='utf-8')
   scripts=re.findall(r'<script src="([^"]+)"[^>]*></script>',html)
   html=re.sub(r'<script[^>]*>.*?</script>','',html,flags=re.S)
   html=re.sub(r'<link[^>]*rel="stylesheet"[^>]*>','',html)
   page.set_content(html)
   page.add_style_tag(content=(args.app/'styles.css').read_text())
   if fixture:
    page.evaluate(FAKE_HOST)
    page.evaluate('(value)=>window.__fixtureAsset=value','data:image/png;base64,'+base64.b64encode((args.app/'assets/logo.png').read_bytes()).decode())
   for script in scripts:page.add_script_tag(content=(args.app/script).read_text(encoding='utf-8'))
  context=browser.new_context()
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('request',lambda r:external.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith('https://ceapp.test/') else None)
  load(page);page.wait_for_timeout(1800)
  assert page.locator('#preview-notice').is_visible();checks.append('hostless preview is explicit')
  assert page.locator('[data-action="probe"]').is_enabled();checks.append('refresh remains usable without host')
  page.select_option('#locale','zh-CN');page.wait_for_timeout(50)
  for width,height in [(1440,1000),(768,1024),(390,844)]:
   page.set_viewport_size({'width':width,'height':height})
   for theme in ['light','dark']:
    page.select_option('#theme',theme)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),(width,theme,'overflow')
    for index in range(9):
     page.locator('#navigation button').nth(index).click()
     assert page.locator('#content h2').is_visible()
     assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    page.locator('#navigation button').nth(0).click()
    page.screenshot(path=str(args.out/f'ui-{width}-{theme}.png'),full_page=True)
    checks.append(f'{width}px/{theme}: all 9 panels, no horizontal overflow')
  page.locator('#navigation button').nth(1).click()
  page.set_input_files('#browser-file',{'name':'demo.txt','mimeType':'text/plain','buffer':'hello \u4e2d\u6587'.encode()})
  page.wait_for_timeout(100);assert 'browser-only' in page.locator('#output').inner_text();checks.append('standalone local file preview works')
  page.select_option('#locale','en-US');page.wait_for_timeout(50);assert 'Files'==page.locator('#content h2').inner_text();checks.append('locale switches UI copy')
  context.close()
  context=browser.new_context();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept());load(page,True);page.wait_for_timeout(300)
  assert not page.locator('#preview-notice').is_visible();checks.append('simulated host detection')
  def click(action):
   page.locator(f'[data-action="{action}"]').click();page.wait_for_timeout(80)
   assert not page.locator('#error-message').is_visible(),(action,page.locator('#output').inner_text())
  page.locator('#navigation button').nth(1).click();click('sample');assert 'sample.csv' in page.locator('#file-list').inner_text()
  page.locator('#navigation button').nth(2).click();click('job-run');assert 'inspection.json' in page.locator('#results').inner_text();click('open-result');click('export-result');checks.append('simulated staged file > job > results > open/export')
  page.locator('#navigation button').nth(3).click();click('runtime-check');checks.append('simulated runtime readiness')
  page.locator('#navigation button').nth(4).click();click('ai-text');assert 'SIMULATED AI RESPONSE' in page.locator('#output').inner_text();checks.append('simulated AI explicit action')
  page.locator('#navigation button').nth(5).click();click('note-save');click('note-read');click('note-list');click('note-delete');checks.append('simulated local CRUD')
  page.locator('#navigation button').nth(6).click();click('phone-session');click('phone-add');click('phone-send');checks.append('simulated phone workflow')
  page.locator('#navigation button').nth(7).click();click('web');click('copy');click('print');click('notify');click('asset');checks.append('simulated web/clipboard/print/notification/asset')
  page.locator('#navigation button').nth(8).click();click('diag');assert 'secret-test' not in page.locator('#output').inner_text();checks.append('diagnostics redacted')
  # A resolved negative envelope must become visible error, not green success.
  page.evaluate('window.CanEngine.requireRuntime=async()=>({ok:false,message:"fixture missing"})')
  page.locator('#navigation button').nth(3).click();page.locator('[data-action="runtime-check"]').click();page.wait_for_timeout(80);assert page.locator('#error-message').is_visible();checks.append('runtime-negative envelope visible')
  assert not errors,errors;assert not external,external
  checks.append('no uncaught page errors; no external startup requests')
  page.screenshot(path=str(args.out/'simulated-error.png'),full_page=True)
  browser.close()
 report={'ok':True,'checks':checks,'uncaughtErrors':errors,'externalStartupRequests':external,'nativeHostTested':False,'assetTransport':'Local HTML/CSS/JS inlined with set_content/add_script_tag. Both file:// and URL navigation are blocked by browser policy; package URL resolution was NOT browser-tested.','fixtureNotice':'Simulated host is test-only; no AI provider, device or native bridge was called.'}
 (args.out/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
