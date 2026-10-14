#!/usr/bin/env python3
"""Real local HTTP/UI, explicitly simulated browser bridge; never submits a site.

Requires Playwright + Chromium. Native CanEngine/target-site acceptance is separate.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import create_ceapp
from test_prefill import FIXTURE

HOST = r"""
window.__calls = []; window.__mode = 'success'; window.__unsubscribed = 0;
window.CanEngine = {
  getLocale:async ()=>'zh-CN',
  onLocaleChange:fn=>{window.__locale=fn; return ()=>{window.__locale=null; window.__unsubscribed++;};},
  browser:{
    openTarget:async target=>{window.__calls.push({action:'open',target});return {open:true,phase:'ready'};},
    prefill:async request=>{
      window.__calls.push({action:'prefill',request});
      if(window.__mode==='timeout') throw new Error('CanEngine Host request timed out');
      if(window.__mode==='denied') throw new Error('BROWSER_PERMISSION_DENIED');
      if(window.__mode==='pending') await new Promise(resolve=>{window.__finish=resolve;});
      const ok=window.__mode!=='negative';
      return {ok, filled:ok?request.fields.length:0, manualRequired:true,
        fields:request.fields.map(field=>({field:field.key,status:ok?'filled':'missing'})), code:ok?'':'FORM_CHANGED'};
    }
  }
};
"""


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--browser',help='Optional local Chromium executable')
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    checks=[]; errors=[]; external=[]
    with tempfile.TemporaryDirectory() as temporary:
        app=create_ceapp.generate(Path(temporary)/'app','ui-prefill','预填测试','form-prefill',
                                 url='https://forms.example.com/contact',mapping=FIXTURE)
        config_path=app/'assets/form-config.json'; config=json.loads(config_path.read_text())
        config['titleI18n']={'zh-CN':'预填测试','en-US':'Prefill Test'}
        config['labels']={'name':{'zh-CN':'姓名','en-US':'Full name'},'country':{'zh-CN':'国家','en-US':'Country'},'city':{'zh-CN':'城市','en-US':'City'}}
        config['options']={'country':[{'value':'SGP','label':{'zh-CN':'新加坡','en-US':'Singapore'}}]}
        config_path.write_text(json.dumps(config,ensure_ascii=False))
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1',0)); port=reservation.getsockname()[1]
        process=subprocess.Popen([sys.executable,str(app/'server.py')],cwd=app,
                                 env={**os.environ,'CANENGINE_PORT':str(port)},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        base='http://127.0.0.1:'+str(port)
        try:
            deadline=time.monotonic()+10
            while True:
                try:
                    with urlopen(base+'/health',timeout=1) as response:
                        assert response.status==200
                    break
                except URLError:
                    if process.poll() is not None or time.monotonic()>deadline:
                        raise RuntimeError('Local fixture backend did not become ready')
                    time.sleep(.05)
            checks.append('Generated Python entry actually starts using CANENGINE_PORT')
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch(executable_path=args.browser or playwright.chromium.executable_path,headless=True)
                context=browser.new_context(); context.add_init_script(HOST)
                page=context.new_page()
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('request',lambda request:external.append(request.url) if not request.url.startswith(base+'/') else None)
                page.goto(base+'/'); page.wait_for_function('!document.getElementById("prefill").disabled')
                assert page.locator('input[name=name]').input_value()=='TEST USER'
                assert page.locator('select[name=country]').input_value()=='SGP'
                for width,height in [(1280,900),(768,900),(390,844)]:
                    for scheme in ['light','dark']:
                        page.set_viewport_size({'width':width,'height':height}); page.emulate_media(color_scheme=scheme)
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                        page.screenshot(path=str(args.out/f'prefill-{width}-{scheme}.png'),full_page=True)
                checks.append('Local assets, bilingual labels/options and six responsive theme layouts')
                page.locator('input[name=name]').fill('SYNTHETIC REVIEW')
                page.evaluate('window.__locale("en-US")')
                assert page.locator('#title').inner_text()=='Prefill Test'
                assert page.locator('input[name=name]').input_value()=='SYNTHETIC REVIEW'
                assert page.locator('select[name=country] option').inner_text()=='Singapore'
                checks.append('Host locale changes preserve in-memory values')
                page.locator('#prefill').click(); page.wait_for_function('!document.getElementById("prefill").disabled')
                assert 'submit yourself' in page.locator('#status').inner_text()
                assert page.locator('#report li').count()==3
                assert page.evaluate('window.__calls[0].request.fields[0].value')=='SYNTHETIC REVIEW'
                assert page.evaluate('Object.keys(window.__calls[0].request).sort().join(",")')=='fields,schemaVersion,scope,target'
                checks.append('Explicit prefill sends public JSON; success keeps final review/submission manual (SIMULATED)')
                page.locator('#open').click(); page.wait_for_function('!document.getElementById("prefill").disabled')
                assert page.evaluate('window.__calls[1].target')=='contact'
                assert page.evaluate('window.__calls[1].action')=='open'
                checks.append('Open website passes only the declared target ID (SIMULATED)')
                page.evaluate('window.__mode="pending"')
                before=page.evaluate('window.__calls.length'); page.locator('#prefill').click()
                page.dispatch_event('#prefill','click'); page.dispatch_event('#open','click')
                assert page.evaluate('window.__calls.length')==before+1
                assert page.locator('#open').is_disabled()
                page.evaluate('window.__mode="success";window.__finish()')
                page.wait_for_function('!document.getElementById("prefill").disabled')
                checks.append('Single-flight blocks duplicate fills and navigation while pending (SIMULATED)')
                page.evaluate('window.__mode="negative"'); page.locator('#prefill').click()
                page.wait_for_function('!document.getElementById("prefill").disabled')
                assert 'manual attention' in page.locator('#status').inner_text()
                assert 'Missing' in page.locator('#report').inner_text()
                checks.append('Resolved ok:false shows changed/missing fields rather than success (SIMULATED)')
                page.evaluate('window.__mode="denied"'); page.locator('#prefill').click()
                page.wait_for_function('!document.getElementById("prefill").disabled')
                assert 'did not complete' in page.locator('#status').inner_text()
                page.evaluate('window.__mode="timeout"'); page.locator('#prefill').click()
                page.wait_for_function('document.getElementById("status").textContent.includes("unconfirmed")')
                count=page.evaluate('window.__calls.length'); page.dispatch_event('#prefill','click')
                assert page.locator('#prefill').is_disabled() and page.locator('#open').is_disabled()
                assert page.evaluate('window.__calls.length')==count
                checks.append('Permission denial is explicit; unknown timeout locks retries (SIMULATED)')
                page.evaluate('window.dispatchEvent(new Event("pagehide"))')
                assert page.evaluate('window.__unsubscribed')==1
                checks.append('Disposal unsubscribes locale handler')
                context.close()
                context=browser.new_context(); page=context.new_page(); page.goto(base+'/')
                page.wait_for_function('document.getElementById("status").textContent.includes("1.8.0")',timeout=7000)
                assert page.locator('#prefill').is_disabled()
                checks.append('No-host preview is bounded and never fabricates success')
                context.close(); browser.close()
        finally:
            process.terminate(); stdout,stderr=process.communicate(timeout=5)
        assert not stdout and not stderr, 'Local backend unexpectedly logged output'
        assert not errors, errors
        assert not external, external
        checks.append('No remote startup requests, backend logs or uncaught UI errors')
    result={'ok':True,'localHttpUi':'PASS','hostBridge':'SIMULATED','nativeCanEngine':'NOT_RUN',
            'actualTargetWebsite':'NOT_RUN','checks':checks,'notice':'Synthetic inputs only. No real target site, native browser bridge, CAPTCHA or final submission was exercised.'}
    (args.out/'prefill-browser-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
