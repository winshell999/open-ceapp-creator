/* Opt-in examples. Copy only the needed functions into a generated app.
   Nothing executes on import. All inputs must originate from authorized host results.
   Confirm installs, sends, registrations and exports in the UI before calling. */
(function(root){
 'use strict';
 const ensure=result=>{if(result?.ok===false)throw new root.CEBridge.BridgeError('HOST_ACTION_FAILED',result.message||result.error);return result;};
 const X={
  file: {
   inspectStaged:(c,id)=>c.call('getStagedFile',[id]),
   removeStaged:(c,id)=>c.mutate('removeStagedFile',[id]).then(ensure),
   nativeSingle:(c)=>c.mutate('stageFileDialog',[c.appId],{timeoutMs:0}),
   nativeMultiple:(c)=>c.mutate('stageFilesDialog',[c.appId],{timeoutMs:0}),
   chooseFolder:(c)=>c.mutate('chooseDirectory',[],{timeoutMs:0}),
   readSmallResult:async(c,file)=>{if(!file?.path || file.size>8*1024*1024)throw new root.CEBridge.BridgeError('FILE_TOO_LARGE');return c.call('resultDataURL',[file.path]);},
   legacySaveAs:(c,authorizedPath)=>c.mutate('saveAs',[authorizedPath],{timeoutMs:0}),
   legacyOpen:(c,authorizedPath)=>c.mutate('openResult',[authorizedPath]),
   legacyReveal:(c,authorizedPath)=>c.mutate('revealResult',[authorizedPath])
  },
  clipboard: {
   text:(c,text)=>c.mutate('clipboard.writeText',[text]),
   imageBlob:(c,blob)=>c.mutate('clipboard.writeImage',[blob]),
   imageDataURL:(c,dataURL)=>c.mutate('copyImageDataURL',[dataURL]),
   resultFile:(c,authorizedPath)=>c.mutate('copyResult',[authorizedPath]),
   saveImage:(c,name,dataURL)=>c.mutate('saveImageDataURL',[name,dataURL],{timeoutMs:0})
  },
  asset: {
   mediaURL:(c,path)=>c.asset(path),
   smallInline:(c,path)=>c.call('assetDataURL',[c.appId,path])
  },
  runtime: {
   list:(c)=>c.call('listRuntimes'),
   check:(c,ids)=>c.call('checkRuntimes',[ids]),
   app:(c)=>c.call('getAppRuntimeStatus',[c.appId]),
   legacyEnvironment:(c)=>c.call('envCheck',[c.appId]),
   legacyInstall:async(c,declaredDependencyId)=>{ensure(await c.mutate('envInstall',[c.appId,declaredDependencyId],{timeoutMs:600000}));return c.call('envCheck',[c.appId]);}
  },
  notification: {
   list:(c)=>c.call('notification.listOwnFeatures'),
   // This registers configuration only. Implement the business producer separately.
   // Never invoke at boot, and never auto-reactivate a deleted/tombstoned feature.
   registerExplicit:(c)=>c.mutate('notification.registerFeature',[{
    featureId:'ceapp-demo-daily',name:'CEAPP demo feature',triggerType:'schedule',entry:'demo.dailyBrief',
    schedule:{type:'interval',everyMinutes:60},level:'info',defaultChannels:['local'],sourceEnabled:true,reactivate:true
   }]).then(ensure),
   disable:(c)=>c.mutate('notification.updateFeature',['ceapp-demo-daily',{sourceEnabled:false}]).then(ensure),
   remove:(c)=>c.mutate('notification.removeFeature',['ceapp-demo-daily']),
   status:(c)=>c.call('notification.getStatus')
  },
  host: {
   identity:(c)=>c.call('getHostVersion'),
   capability:(c,verifiedCapabilityId)=>c.call('hasCapability',[verifiedCapabilityId]),
   print:(c,html)=>c.mutate('print',[html,{}],{timeoutMs:0}),
   diagnostics:(c)=>c.call('getDiagnostics',[c.appId]),
   // Host copy/export may contain private diagnostics. Review before sharing.
   copyDiagnostics:(c)=>c.mutate('copyDiagnostics',[c.appId]),
   exportDiagnostics:(c)=>c.mutate('exportDiagnostics',[c.appId],{timeoutMs:0})
  }
 };
 root.CEBridgeExamples=X;
})(typeof globalThis!=='undefined'?globalThis:this);
