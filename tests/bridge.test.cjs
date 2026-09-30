'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');const path=require('node:path');
const B=require('../assets/starter/assets/ce-bridge.js');global.CEBridge=B;const R=require('../assets/starter/assets/recipes.js');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const make=(host={})=>new B.Client({appId:'test-app',window:{CanEngine:host},timeoutMs:50});
const expectCode=(promise,code)=>assert.rejects(promise,e=>e.code===code);
function jobHost(mode='success'){
 const listeners=new Map(),state={calls:0,info:null,cancelled:false};
 const host={requireRuntime:async()=>({ok:true}),listJobs:async()=>state.info?[state.info]:[],
  onEvent:(name,fn)=>{const list=listeners.get(name)||new Set();list.add(fn);listeners.set(name,list);return()=>list.delete(fn);},
  emit:(name,value)=>{for(const fn of listeners.get(name)||[])fn(value);},
  getJob:async()=>state.info,
  cancelJob:async id=>{assert.equal(id,state.info.id);state.cancelled=true;},
  runJob:async request=>{state.calls++;assert.equal(request.appId,'test-app');
   host.emit('job:started',{id:'foreign',appId:'other-app',commandId:'inspect',status:'running'});
   state.info={id:'job-1',appId:'test-app',commandId:'inspect',status:'running',ok:false,files:[]};host.emit('job:started',state.info);
   if(mode==='queued'){setTimeout(()=>{state.info={...state.info,status:'success',ok:true};},20);return state.info;}
   await delay(20);state.info={...state.info,status:state.cancelled?'cancelled':mode,ok:!state.cancelled&&mode==='success',error:mode==='failed'?'failure':undefined};
   host.emit(state.cancelled?'job:cancelled':'job:completed',state.info);return state.info;
  }};return {host,state,listeners};
}
test('cross-origin parent never crashes detection',()=>{const win={};Object.defineProperty(win,'parent',{get(){throw Error('SecurityError');}});assert.equal(B.discover(win),null);});
test('hostless call is explicit, never fake success',async()=>{await expectCode(new B.Client({appId:'x',window:{}}).call('chooseFile'),'HOST_UNAVAILABLE');});
test('delayed bridge injection is awaited',async()=>{const w={};const c=new B.Client({appId:'x',window:w});setTimeout(()=>w.CanEngine={},20);assert.equal(await c.ready(100),true);});
test('disabled parent resolution prevents outer context reuse',()=>{assert.equal(B.discover({parent:{CanEngine:{}}},false),null);});
test('method owner binding is retained',async()=>{assert.equal(await make({ai:{label:'ok',getStatus(){return this.label;}}}).call('ai.getStatus'),'ok');});
test('resolved runtime failure is rejected',async()=>{await expectCode(make({requireRuntime:async()=>({ok:false,message:'missing'})}).requireRuntime('python-runtime'),'RUNTIME_NOT_READY');});
test('native picker cancellation is an empty selection',async()=>{assert.deepEqual(await make({chooseFile:async()=>null}).chooseFiles(),[]);});
test('picker uses real object request',async()=>{const c=make({chooseFile:async r=>{assert.equal(r.appId,'test-app');return{id:'f1',name:'a'};}});assert.equal((await c.chooseFiles())[0].id,'f1');});
test('picker does not turn malformed envelopes into a file',async()=>{await expectCode(make({chooseFile:async()=>({ok:false})}).chooseFiles(),'FILE_PICK_FAILED');});
test('legacy picker used only if current method absent',async()=>{assert.equal((await make({stageFileDialog:async id=>({id,name:id})}).chooseFiles())[0].name,'test-app');});
test('denial never falls back to a second native picker',async()=>{let legacy=0;const c=make({chooseFile:async()=>{throw{code:'PERMISSION_DENIED'};},stageFileDialog:()=>legacy++});await expectCode(c.chooseFiles(),'PERMISSION_DENIED');assert.equal(legacy,0);});
test('mutations are single-flight',async()=>{const c=make({send:()=>delay(20)});const first=c.mutate('send');await expectCode(c.mutate('send'),'IN_FLIGHT');await first;});
test('mutation timeout remains locked through late settlement until reconciliation',async()=>{const c=make({send:async()=>{await delay(20);return{taskId:'late'};}});await expectCode(c.mutate('send',[],{timeoutMs:3}),'OUTCOME_UNKNOWN');await delay(30);await expectCode(c.mutate('send'),'IN_FLIGHT');assert.equal(c.recoverOutcome('send').taskId,'late');assert.equal(c.unknown.size,0);});
test('read timeout is not reported as cancelled execution',async()=>{await expectCode(make({read:()=>delay(100)}).call('read',[],{timeoutMs:3}),'TIMEOUT');});
test('safe URLs reject dangerous schemes and embedded credentials',()=>{for(const u of ['javascript:alert(1)','file:///etc/passwd','data:text/html,x','https://user:pass@example.com','not-a-url'])assert.throws(()=>B.safeHTTPURL(u),e=>e.code==='INVALID_URL');assert.equal(B.safeHTTPURL('https://example.com'),'https://example.com/');});
test('diagnostic redaction removes credential fields and token query',()=>{const s=JSON.stringify(B.clean({apiKey:'secret',sessionId:'sid',url:'https://x.test/?token=aaa',sourcePath:'/Users/a/private'}));assert(!s.includes('aaa'));assert(!s.includes('secret'));assert(!s.includes('/Users/'));});
test('result references cannot borrow a foreign file object',()=>{assert.throws(()=>make().resultReference({id:'j',files:[]},{fileRef:'f'}),e=>e.code==='INVALID_RESULT_REFERENCE');});
test('result action prefers fileRef and jobId over paths',async()=>{const file={fileRef:'ref',path:'/path',name:'a'},job={id:'j',files:[file]};await make({exportFile:async r=>{assert.equal(r.jobId,'j');assert.equal(r.fileRef,'ref');assert(!r.sourcePath);}}).resultAction('exportFile',job,file);});
test('resolved result-action failure is an error',async()=>{const f={fileRef:'r'};await expectCode(make({openFile:async()=>({ok:false})}).resultAction('openFile',{id:'j',files:[f]},f),'RESULT_ACTION_FAILED');});
test('data factory is synchronous and methods retain this',async()=>{const c=make({data:{local:()=>({get(){return this.x},find(){return[]},put(){},delete(){},x:12})}});assert.equal(await c.storeCall('notes','get','n'),12);});
test('async data factory is a contract error',()=>{assert.throws(()=>make({data:{local:async()=>({})}}).store('x'),e=>e.code==='CONTRACT_MISMATCH');});
test('data put false envelope is not success',async()=>{const c=make({data:{local:()=>({get(){},find(){},delete(){},put(){return{ok:false};}})}});await expectCode(c.storeCall('x','put',{}),'DATA_OPERATION_FAILED');});
test('phone file identifier is not treated as staged identifier',async()=>{await expectCode(make().phoneToStaged({id:'wrong'}),'INVALID_PHONE_FILE');});
test('packaged asset path traversal rejected',async()=>{await expectCode(make().asset('../secret'),'INVALID_ASSET_PATH');});
test('AI text request shape and text validation',async()=>{const c=make({ai:{text:{generate:async r=>{assert.equal(r.messages[0].role,'user');assert.equal(r.maxTokens,400);return{text:'ok'};}}}});assert.equal((await R.text(c,'hello')).text,'ok');});
test('AI missing text envelope fails loudly',async()=>{await expectCode(R.text(make({ai:{text:{generate:async()=>({})}}}),'hi'),'CONTRACT_MISMATCH');});
test('video uses create and the singular inputImage',async()=>{const c=make({ai:{video:{create:async r=>{assert.equal(r.inputImage.type,'temp-file');assert(!r.inputImages);return{taskId:'v1',status:'queued'};}}}});const m=new R.MediaTask(c);assert.equal((await m.create('video','bird',{path:'/staged'})).taskId,'v1');});
test('shared dataset requires exact declared ID',async()=>{await expectCode(R.dataset(make(),{datasets:[]},'invented'),'UNDECLARED_DATASET');});
test('phone callback failures are contained',async()=>{let callback,seen;const c=make({phoneBridge:{onFilesReceived:fn=>{callback=fn;return()=>{};}}});const off=R.receive(c,async()=>{throw Error('bad file')},e=>seen=e.message);callback([]);await delay(0);assert.equal(seen,'bad file');off();});
test('blocking runJob captures ID before completion and supports cancellation',async()=>{const{host,state,listeners}=jobHost();const c=make(host),j=new B.JobController(c);const p=j.run('inspect',['f']);await delay(5);assert.equal(j.current.id,'job-1');assert.equal(j.busy,true);await j.cancel();await expectCode(p,'CANCELLED');assert.equal(state.calls,1);assert.equal(j.busy,false);assert([...listeners.values()].every(set=>set.size===0));});
test('job envelope failure is not success',async()=>{const{host}=jobHost('failed');await expectCode(new B.JobController(make(host)).run('inspect',['f']),'JOB_FAILED');});
test('parallel job submissions are blocked',async()=>{const{host,state}=jobHost();const j=new B.JobController(make(host)),p=j.run('inspect',['f']);await expectCode(j.run('inspect',['f']),'IN_FLIGHT');await p;assert.equal(state.calls,1);});
test('runtime failure blocks job execution',async()=>{let calls=0;const j=new B.JobController(make({requireRuntime:async()=>({ok:false}),runJob:()=>calls++}));await expectCode(j.run('inspect'),'RUNTIME_NOT_READY');assert.equal(calls,0);assert.equal(j.busy,false);});
test('queued host response keeps lock until polled terminal state',async()=>{const{host}=jobHost('queued');const j=new B.JobController(make(host));const p=j.run('inspect',['f'],[],{timeoutMs:2000});await delay(5);assert.equal(j.busy,true);await p;assert.equal(j.busy,false);});
test('job timeout is unknown and late completion unlocks',async()=>{const{host}=jobHost();const j=new B.JobController(make(host));await expectCode(j.run('inspect',['f'],[],{timeoutMs:2}),'OUTCOME_UNKNOWN');assert.equal(j.busy,true);await delay(30);assert.equal(j.busy,false);assert.equal(j.current.status,'success');});
test('subscriptions are removed on client disposal',()=>{let count=0;const c=make({onLocaleChange:()=>()=>count++});c.subscribe('onLocaleChange',()=>{});c.dispose();assert.equal(count,1);});
test('all English and Chinese message keys have parity',()=>{const {messages}=require('../assets/starter/assets/ceapp-i18n.js');assert.deepEqual(Object.keys(messages['en-US']).sort(),Object.keys(messages['zh-CN']).sort());});
