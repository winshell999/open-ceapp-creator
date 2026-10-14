(function(root){
  'use strict';
  const B=root.CEBridge;
  function check(result, code='HOST_ACTION_FAILED') { if(result?.ok===false)throw new B.BridgeError(code,result.message||result.error);return result; }
  async function text(client,prompt){
    if(!String(prompt).trim())throw new B.BridgeError('INPUT_REQUIRED');
    const value=await client.mutate('ai.text.generate',[{messages:[{role:'user',content:prompt}],maxTokens:400}],{timeoutMs:120000});
    check(value,'AI_FAILED');if(typeof value?.text!=='string')throw new B.BridgeError('CONTRACT_MISMATCH','AI response.text missing');return value;
  }
  async function vision(client,prompt,staged){
    if(!staged?.path)throw new B.BridgeError('INPUT_REQUIRED','Choose an image');
    return check(await client.mutate('ai.vision.analyze',[{prompt,images:[{type:'temp-file',path:staged.path}],maxTokens:400}],{timeoutMs:120000}));
  }
  async function image(client,prompt){
    return check(await client.mutate('ai.image.generate',[{prompt,size:'1024x1024',count:1}],{timeoutMs:180000}));
  }
  class MediaTask {
    constructor(client,onChange=()=>{}){this.client=client;this.onChange=onChange;this.task=null;this.waiting=false;this.stopped=false;this.submitting=false;this.kind='video';}
    async create(kind,prompt,staged){
      if(this.submitting || (this.task && !B.terminal(this.task.status)))throw new B.BridgeError('IN_FLIGHT');
      this.kind=kind;this.submitting=true;
      const media=staged?.path?{type:'temp-file',path:staged.path}:null;
      const method=kind==='video'?'ai.video.create':'ai.model3d.generate';
      const request=kind==='video'?{prompt,...(media?{inputImage:media}:{}),durationSeconds:4,ratio:'16:9',quality:'preview'}:{prompt,inputImages:media?[media]:[],outputFormat:'glb',quality:'preview'};
      try{const task=check(await this.client.mutate(method,[request],{timeoutMs:180000,key:'media-create'}));
        if(!task?.taskId)throw new B.BridgeError('CONTRACT_MISMATCH','Media taskId missing');this.task=task;this.onChange(task);return task;
      }finally{this.submitting=false;}
    }
    async refresh(){
      if(!this.task?.taskId)throw new B.BridgeError('INPUT_REQUIRED','No media task');
      const task=check(await this.client.call('ai.'+this.kind+'.getTask',[this.task.taskId]));
      this.task={...task,taskId:this.task.taskId};this.onChange(this.task);return this.task;
    }
    async wait({timeoutMs=600000,intervalMs=2000}={}){
      if(this.waiting)throw new B.BridgeError('IN_FLIGHT');this.waiting=true;this.stopped=false;const deadline=Date.now()+timeoutMs;
      try{while(!this.stopped&&Date.now()<deadline){const task=await this.refresh();if(B.terminal(task.status))return task;await new Promise(r=>setTimeout(r,intervalMs));}
        throw new B.BridgeError('WAIT_STOPPED','Polling stopped; the host task may still run. Use Refresh or Cancel.');
      }finally{this.waiting=false;}
    }
    async cancel(){if(!this.task?.taskId)throw new B.BridgeError('INPUT_REQUIRED');await this.client.mutate('ai.'+this.kind+'.cancelTask',[this.task.taskId]);return this.refresh();}
    stopWaiting(){this.stopped=true;}
  }
  async function dataset(client,config,id){
    if(!config.datasets.includes(id))throw new B.BridgeError('UNDECLARED_DATASET','Declare the exact dataset ID in app.json and app-config.js first');
    const host=client.host();if(typeof host?.data?.dataset!=='function')throw new B.BridgeError('CAPABILITY_UNAVAILABLE');
    return check(await client.effect('dataset-read',()=>host.data.dataset(id).find({limit:20})), 'DATA_OPERATION_FAILED');
  }
  async function action(client,config,id,params){
    if(!config.actions.includes(id))throw new B.BridgeError('UNDECLARED_ACTION','Declare and authorize the exact action ID first');
    return check(await client.mutate('data.action',[id,params]));
  }
  function receive(client,onFiles,onError){
    return client.subscribe('phoneBridge.onFilesReceived',files=>{
      Promise.resolve().then(()=>onFiles(Array.isArray(files)?files:[])).catch(onError);
    });
  }
  root.CERecipes={check,text,vision,image,MediaTask,dataset,action,receive};
  if(typeof module==='object'&&module.exports)module.exports=root.CERecipes;
})(typeof globalThis!=='undefined'?globalThis:this);
