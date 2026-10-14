/* CEAPP public bridge adapter. No Wails internals, server URLs or mock results. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CEBridge = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  class BridgeError extends Error {
    constructor(code, message, details) {
      super(message || code); this.name = 'BridgeError'; this.code = code;
      this.details = details || null;
    }
  }
  const fail = (code, message, details) => new BridgeError(code, message, details);
  const terminal = s => ['success','succeeded','completed','failed','error','cancelled','canceled'].includes(String(s).toLowerCase());
  const successful = s => ['success','succeeded','completed'].includes(String(s).toLowerCase());
  function clean(value, depth = 0, seen = new WeakSet()) {
    if (depth > 5) return '[depth-limit]';
    if (typeof value === 'string') return value
      .replace(/data:[^\s]+/g, '[data-omitted]')
      .replace(/(Bearer\s+)[^\s]+/gi, '$1[redacted]')
      .replace(/([?&](?:token|key|sid|sessionId|code)=)[^&\s]+/gi, '$1[redacted]')
      .replace(/(?:\/Users\/|\/home\/|[A-Z]:\\)[^\s"<>]*/g, '[local-path]')
      .slice(0, 1400);
    if (!value || typeof value !== 'object') return value;
    if (seen.has(value)) return '[circular]'; seen.add(value);
    if (Array.isArray(value)) return value.slice(0, 40).map(v => clean(v, depth + 1, seen));
    const result = {};
    for (const [key, v] of Object.entries(value).slice(0, 60)) {
      if (/token|secret|password|authorization|api.?key|qr|session|data(base64|url)|sourcepath|localpath|stdout|stderr|command|cwd/i.test(key)) result[key] = '[redacted]';
      else result[key] = clean(v, depth + 1, seen);
    }
    return result;
  }
  function normalizeError(error) {
    if (error instanceof BridgeError) return error;
    let value = error;
    if (typeof error === 'string') { try { value = JSON.parse(error); } catch (_) {} }
    const code = value && (value.code || value.errorCode || value.error?.code);
    const message = typeof value === 'string' ? value : (value?.message || value?.error?.message || 'Host call failed');
    return fail(code || 'HOST_ERROR', clean(String(message)));
  }
  function safeHTTPURL(raw) {
    let url;
    try { url = new URL(String(raw).trim()); } catch (_) { throw fail('INVALID_URL', 'Enter a complete HTTP(S) URL'); }
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) throw fail('INVALID_URL', 'Only HTTP(S) URLs without credentials are allowed');
    return url.href;
  }
  function discover(win, allowParent = true) {
    try { if (win?.CanEngine) return win.CanEngine; } catch (_) {}
    if (allowParent) { try { if (win?.parent && win.parent !== win && win.parent.CanEngine) return win.parent.CanEngine; } catch (_) {} }
    return null;
  }
  function targetAt(host, path) {
    const parts = path.split('.'); const name = parts.pop(); let owner = host;
    for (const part of parts) owner = owner?.[part];
    return { owner, fn: owner?.[name] };
  }
  function bounded(promise, ms, sideEffect) {
    if (!ms) return promise;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(fail(sideEffect ? 'OUTCOME_UNKNOWN' : 'TIMEOUT',
        sideEffect ? 'The host has not replied. Do not resubmit; inspect the task or reconcile the result.' : 'The host did not reply in time.')), ms);
      promise.then(v => { clearTimeout(timer); resolve(v); }, e => { clearTimeout(timer); reject(e); });
    });
  }
  function utf8Base64(text) {
    const bytes = new TextEncoder().encode(text); let binary = '';
    for (let i = 0; i < bytes.length; i += 8192) binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
    return btoa(binary);
  }
  function fileDataURL(blob, maxBytes = 8 * 1024 * 1024) {
    if (!blob || typeof blob.size !== 'number' || blob.size > maxBytes) return Promise.reject(fail('FILE_TOO_LARGE', 'Use the native file picker for files larger than 8 MiB.'));
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(fail('FILE_READ_FAILED', 'Unable to read this file'));
      reader.onabort = () => reject(fail('CANCELLED', 'Read cancelled'));
      reader.onload = () => resolve(String(reader.result)); reader.readAsDataURL(blob);
    });
  }
  class Client {
    constructor({appId, window: win, allowParent = true, timeoutMs = 15000} = {}) {
      if (!/^[a-z0-9][a-z0-9-]*$/.test(appId || '')) throw fail('INVALID_APP_ID');
      this.appId = appId; this.win = win || (typeof window !== 'undefined' ? window : {});
      this.allowParent = allowParent; this.timeoutMs = timeoutMs; this.pending = new Map();
      this.unknown = new Map(); this.logs = []; this.disposers = new Set(); this.disposed = false;
    }
    host() { return discover(this.win, this.allowParent); }
    has(path) { return typeof targetAt(this.host(), path).fn === 'function'; }
    record(method, outcome, data) { this.logs.push({time:new Date().toISOString(),method,outcome,data:clean(data)}); this.logs = this.logs.slice(-60); }
    async ready(waitMs = 1600) {
      const end = Date.now() + waitMs;
      do { if (this.disposed) return false; if (this.host()) return true; await new Promise(r => setTimeout(r, 40)); } while (Date.now() < end);
      return false;
    }
    raw(path, args = []) {
      if (this.disposed) return Promise.reject(fail('DISPOSED'));
      const {owner, fn} = targetAt(this.host(), path);
      if (typeof fn !== 'function') return Promise.reject(fail(this.host() ? 'CAPABILITY_UNAVAILABLE' : 'HOST_UNAVAILABLE', path));
      return Promise.resolve().then(() => fn.apply(owner, args)).catch(e => { throw normalizeError(e); });
    }
    async call(path, args = [], options = {}) {
      try { const result = await bounded(this.raw(path, args), options.timeoutMs ?? this.timeoutMs, false);
        this.record(path, 'returned', {type:typeof result}); return result;
      } catch (e) { this.record(path,'failed',normalizeError(e).code); throw normalizeError(e); }
    }
    async mutate(path, args = [], {key = path, timeoutMs = this.timeoutMs} = {}) {
      return this.effect(key, () => this.raw(path, args), timeoutMs);
    }
    async effect(key, run, timeoutMs = this.timeoutMs) {
      if (this.pending.has(key) || this.unknown.has(key)) throw fail('IN_FLIGHT', 'This action is still pending. Do not submit it again.');
      const operation = Promise.resolve().then(run);
      const outcome = {state:'pending'};
      this.pending.set(key, operation);
      operation.then(value => { outcome.state='returned';outcome.value=value;this.pending.delete(key);this.record(key,'settled'); }, e => {outcome.state='failed';outcome.error=normalizeError(e);this.pending.delete(key);this.record(key,'failed',normalizeError(e).code);});
      try { return await bounded(operation, timeoutMs, true); } catch(e) { if(e.code==='OUTCOME_UNKNOWN')this.unknown.set(key,outcome);throw normalizeError(e); }
    }
    recoverOutcome(key) {
      const outcome=this.unknown.get(key);
      if(!outcome || outcome.state==='pending')throw fail('IN_FLIGHT','The host has not returned a reconciled outcome.');
      this.unknown.delete(key);if(outcome.state==='failed')throw outcome.error;return outcome.value;
    }
    subscribe(path, ...args) {
      const {owner, fn} = targetAt(this.host(), path);
      if (typeof fn !== 'function') throw fail('CAPABILITY_UNAVAILABLE', path);
      let unsub;
      try { unsub = fn.apply(owner, args); } catch (e) { throw normalizeError(e); }
      if (typeof unsub !== 'function') throw fail('CONTRACT_MISMATCH', path + ' must return an unsubscribe function');
      const off = () => { this.disposers.delete(off); try { unsub(); } catch (_) {} };
      this.disposers.add(off); return off;
    }
    async probe(paths = []) {
      const read = async p => this.has(p) ? this.call(p).then(value => ({state:'returned',value}),error => ({state:'failed',code:error.code})) : {state:'unavailable'};
      return {hostPresent:!!this.host(), version:await read('getHostVersion'), capabilities:await read('getCapabilities'), methods:Object.fromEntries(paths.map(p => [p,this.has(p)]))};
    }
    async requireRuntime(id) {
      const report = await this.call('requireRuntime',[id]);
      if (!report || report.ok !== true) throw fail('RUNTIME_NOT_READY', report?.message || id, report);
      return report;
    }
    async chooseFiles(multiple = false) {
      const method = multiple ? 'chooseFiles' : 'chooseFile';
      let result;
      if (this.has(method)) result = await this.mutate(method,[{appId:this.appId}],{timeoutMs:0});
      else result = await this.mutate(multiple ? 'stageFilesDialog' : 'stageFileDialog',[this.appId],{timeoutMs:0});
      if (result == null) return []; // Native dialog cancel is not an exception.
      if (result.ok === false) throw fail('FILE_PICK_FAILED', result.message);
      const files = multiple ? result : [result];
      if (!Array.isArray(files) || files.some(f => !f || typeof f.id !== 'string' || !f.id)) throw fail('CONTRACT_MISMATCH','Expected staged file IDs');
      return files;
    }
    async stageBlob(blob, name) {
      const dataBase64 = await fileDataURL(blob);
      const result = await this.mutate('stageFile',[{appId:this.appId,name:name || blob.name || 'input.bin',mime:blob.type || 'application/octet-stream',dataBase64}]);
      if (!result?.id) throw fail('CONTRACT_MISMATCH','stageFile returned no ID'); return result;
    }
    async stagePath(sourcePath) {
      if (typeof sourcePath !== 'string' || !sourcePath) throw fail('INVALID_FILE');
      const result = await this.mutate('stageFile',[{appId:this.appId,sourcePath}]);
      if (!result?.id) throw fail('CONTRACT_MISMATCH','stageFile returned no ID'); return result;
    }
    async sample() {
      const result = await this.mutate('stageFile',[{appId:this.appId,name:'sample.csv',mime:'text/csv',dataBase64:utf8Base64('name,value\nCanEngine,42\nDemo,7\n')}]);
      if (!result?.id) throw fail('CONTRACT_MISMATCH','stageFile returned no ID'); return result;
    }
    resultReference(job, file) {
      if (!job?.id || !file || !(job.files || []).includes(file)) throw fail('INVALID_RESULT_REFERENCE','Select a file from this job');
      if (file.fileRef) return {jobId:job.id,fileRef:file.fileRef,suggestedName:file.name};
      if (file.path) return {sourcePath:file.path,suggestedName:file.name};
      throw fail('INVALID_RESULT_REFERENCE');
    }
    async resultAction(action, job, file, directory) {
      const ref = this.resultReference(job,file);
      if (!['openFile','revealFile','exportFile'].includes(action)) throw fail('INVALID_ACTION');
      if (directory) {
        if (!directory.id || directory.writable === false) throw fail('DIRECTORY_NOT_WRITABLE');
        ref.targetDirectoryId = directory.id;
      }
      const result = await this.mutate(action,[ref],{timeoutMs:action === 'exportFile' ? 0 : this.timeoutMs});
      if (result?.ok === false) throw fail('RESULT_ACTION_FAILED',result.message);
      return result; // Export cancellation is reported without claiming a file was saved.
    }
    store(collection) {
      const {owner,fn} = targetAt(this.host(),'data.local');
      if (typeof fn !== 'function') throw fail('CAPABILITY_UNAVAILABLE','data.local');
      const store = fn.call(owner,collection);
      for (const key of ['get','find','put','delete']) if (typeof store?.[key] !== 'function') throw fail('CONTRACT_MISMATCH','data.local is a synchronous collection factory');
      return store;
    }
    async storeCall(collection, operation, ...args) {
      const store = this.store(collection);
      if (!['get','find','put','delete'].includes(operation)) throw fail('INVALID_ACTION');
      const run = () => Promise.resolve().then(() => store[operation](...args));
      const result = ['put','delete'].includes(operation) ? await this.effect('data.'+collection+'.'+operation,run) : await bounded(run(),this.timeoutMs,false);
      if (result?.ok === false) throw fail('DATA_OPERATION_FAILED',result.message); return result;
    }
    async phoneToStaged(file) {
      if (!file?.fileId) throw fail('INVALID_PHONE_FILE');
      if (Number(file.size) > 8*1024*1024) throw fail('FILE_TOO_LARGE','Use the Phone Bridge workbench for large files');
      const blob = await this.call('phoneBridge.readFile',[file.fileId]);
      return this.stageBlob(blob,file.name);
    }
    async asset(path) {
      if (/^(?:[a-z]+:|\/|\\)/i.test(path) || path.split(/[\\/]/).includes('..')) throw fail('INVALID_ASSET_PATH');
      if (this.host()) return this.call('assetURL',[this.appId,path]);
      return path; // Only standalone browsers use the relative fallback.
    }
    dispose() { this.disposed = true; for (const off of [...this.disposers]) off(); }
  }
  class JobController {
    constructor(client, onChange = () => {}) { this.client = client;this.onChange = onChange;this.current = null;this.busy = false;this.offs = [];this.candidates = new Set();this.uncertain = false;this.disposed = false; }
    notify() { try { this.onChange(this.current,this); } catch(e) {this.client.record('job-ui','failed',normalizeError(e).code);} }
    async run(commandId, inputFileIds = [], args = [], options = {}) {
      if (this.busy) throw fail('IN_FLIGHT');
      this.busy = true;this.current = null;this.runPromise=null;this.candidates.clear();this.uncertain = false;this.notify();
      let before = new Set();
      try {
        await this.client.requireRuntime('python-runtime');
        const jobs = await this.client.call('listJobs',[{appId:this.client.appId,limit:100}]);
        if (!Array.isArray(jobs)) throw fail('CONTRACT_MISMATCH','listJobs must return an array');
        before = new Set(jobs.map(j => j.id));
        if (jobs.some(j => j.commandId === commandId && !terminal(j.status))) throw fail('EXISTING_JOB','A task with this command is already active; inspect it first.');
        // The legacy started event carries appId and commandId; the dotted one does not.
        if (this.client.has('onEvent')) {
          this.offs.push(this.client.subscribe('onEvent','job:started', info => {
            if (this.disposed || !info?.id || info.appId !== this.client.appId || info.commandId !== commandId || before.has(info.id)) return;
            this.candidates.add(info.id);this.current = info;this.notify();
          }));
          for (const event of ['job:completed','job:failed','job:cancelled']) this.offs.push(this.client.subscribe('onEvent',event,info => {
            if (!this.disposed && info?.id === this.current?.id) {this.current = info;this.notify();}
          }));
        }
        const promise = this.client.raw('runJob',[{appId:this.client.appId,commandId,inputFileIds,args,...(options.mode ? {mode:options.mode} : {})}]);
        this.runPromise = promise;
        promise.then(info => {this.current = info;if(terminal(info?.status))this.finish();else this.notify();}, () => this.finish());
        let info = await bounded(promise, options.timeoutMs ?? 15*60*1000, true);
        if (!info?.id) throw fail('CONTRACT_MISMATCH','runJob returned no job ID');
        if (!terminal(info.status)) {
          // Forward-compatible queued/running response: keep ownership lock until terminal.
          this.busy = true; const end = Date.now() + (options.timeoutMs ?? 15*60*1000);
          do { if (this.disposed) throw fail('DISPOSED'); await new Promise(r=>setTimeout(r,400)); try{info=await this.client.call('getJob',[info.id]);}catch(e){this.uncertain=true;throw fail('OUTCOME_UNKNOWN','Task polling failed; inspect the job before retrying.');} this.current=info;this.notify(); }
          while (!terminal(info.status) && Date.now()<end);
          if (!terminal(info.status)) {this.uncertain=true;throw fail('OUTCOME_UNKNOWN','Stop waiting is not cancellation. Inspect this job before resubmitting.');}
          this.finish();
        }
        this.current = info;this.notify();
        if (info.status === 'cancelled' || info.status === 'canceled') throw fail('CANCELLED','Task cancelled');
        if (info.ok === false || !successful(info.status)) throw fail('JOB_FAILED',info.error || 'Inspect task logs');
        if (!Array.isArray(info.files)) throw fail('CONTRACT_MISMATCH','Job files missing');
        return info;
      } catch (error) {
        if (error.code === 'OUTCOME_UNKNOWN') {this.uncertain = true;this.notify();}
        else if (!this.runPromise || !this.uncertain) this.finish();
        throw normalizeError(error);
      }
    }
    finish() { this.busy=false;this.uncertain=false; for(const off of this.offs.splice(0)) off();if(!this.disposed)this.notify(); }
    async refresh() {
      if (!this.current?.id) throw fail('JOB_ID_PENDING','Waiting for a verified job ID');
      const info=await this.client.call('getJob',[this.current.id]); this.current=info;
      if(terminal(info.status))this.finish();this.notify();return info;
    }
    async cancel() {
      if (!this.current?.id || terminal(this.current.status)) throw fail('NO_ACTIVE_JOB');
      if(this.candidates.size>1)throw fail('AMBIGUOUS_JOB','More than one matching job started. Select and inspect the task in the host.');
      const jobs=await this.client.call('listJobs',[{appId:this.client.appId,limit:100}]);
      const matching=jobs.filter(j=>j.commandId===this.current.commandId && !terminal(j.status));
      if(matching.length!==1 || matching[0].id!==this.current.id)throw fail('AMBIGUOUS_JOB','Cannot safely identify the task to cancel');
      await this.client.mutate('cancelJob',[this.current.id]);
      // An acknowledgement is not a terminal state. Re-read before showing cancelled.
      return this.refresh();
    }
    dispose() {this.disposed=true;for(const off of this.offs.splice(0))off();} // Never cancel silently on navigation.
  }
  return {Client,JobController,BridgeError,normalizeError,clean,safeHTTPURL,utf8Base64,fileDataURL,terminal,successful,discover};
});
