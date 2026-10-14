"""Structural Web manifest checks; CanEngine remains the authoritative gate."""
import ipaddress
from pathlib import Path, PurePosixPath
import re
from urllib.parse import parse_qsl, urlsplit

def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+\.\d+\.\d+', value):
        return (0, 0, 0)
    return tuple(map(int, value.split('.')))

def origin(raw, exact=False):
    if not isinstance(raw, str) or raw != raw.strip() or any(c in raw for c in ('\\', '\r', '\n', '\x00')):
        raise ValueError('Invalid website URL')
    u = urlsplit(raw)
    host = (u.hostname or '').lower()
    if not host or u.username is not None or u.password is not None or any(c.isspace() or c == '*' for c in host):
        raise ValueError('Use a valid URL without credentials or wildcards')
    try: loopback = ipaddress.ip_address(host).is_loopback
    except ValueError: loopback = False
    if u.scheme != 'https' and not (u.scheme == 'http' and loopback):
        raise ValueError('HTTPS required; HTTP is only allowed for numeric loopback development')
    if exact and (u.path not in ('', '/') or u.query or u.fragment):
        raise ValueError('allowedOrigins must contain exact origins without paths or parameters')
    port = u.port
    if (u.scheme == 'https' and port == 443) or (u.scheme == 'http' and port == 80): port = None
    if ':' in host: host = '[' + host + ']'
    return u.scheme + '://' + host + (':' + str(port) if port is not None else '')

def validate_web(manifest, root):
    errors = []
    def require(ok, message):
        if not ok: errors.append(message)
    runtime = manifest.get('runtime') or {}
    remote = runtime.get('remoteWeb')
    web = runtime.get('web')
    if remote is not None:
        require(isinstance(remote, dict), 'remoteWeb must be an object')
        if not isinstance(remote, dict): return errors
        require(set(remote) <= {'url','allowedOrigins','storage','authorization'}, 'Unsupported remoteWeb field; website keys and license credentials must not be packaged')
        authorization = remote.get('authorization','')
        require(authorization in ('','canengine'), 'remoteWeb.authorization supports only canengine')
        private_fields = {'appkey','serverkey','licensetoken','licensekey','admintoken','ticket'}
        require(not any(re.sub(r'[_-]', '', key.lower()) in private_fields for key in manifest), 'Remote manifest contains server-only credentials')
        require(web is None, 'runtime.web and runtime.remoteWeb are mutually exclusive')
        require(version(manifest.get('minCanEngineVersion')) >= (1,8,0), 'remoteWeb requires CanEngine 1.8.0+')
        require(manifest.get('entry', '') in ('', 'app.json'), 'Remote entry must be omitted or app.json')
        require(not manifest.get('commands'), 'Remote websites cannot declare local commands')
        require(manifest.get('environment') is None and not runtime.get('requirements'), 'Remote websites cannot declare a local execution environment')
        require(manifest.get('capabilities') is None and manifest.get('fileDialog') is None, 'Remote websites do not have a Host Bridge or native host file contract')
        require(manifest.get('permissions') == ['web.network'], 'Remote websites require only web.network')
        require(remote.get('storage','persistent') in ('','persistent','ephemeral'), 'Invalid remote storage mode')
        try:
            origin(remote.get('url'))
            if authorization == 'canengine':
                u = urlsplit(remote['url'])
                require(bool(u.path) and not u.fragment, 'Protected entry needs an explicit path and no fragment, matching website registration')
                query_keys = {re.sub(r'[_-]', '', key.lower()) for key, _ in parse_qsl(u.query)}
                require(not query_keys.intersection(private_fields | {'token','authorization'}), 'Credentials and tickets must not appear in a protected entry URL')
                require(bool(re.fullmatch(r'[a-z0-9][a-z0-9._-]{1,63}',manifest.get('appId',''))), 'Protected website registration needs an appId of 2-64 characters')
        except ValueError as exc: errors.append(str(exc))
        origins = remote.get('allowedOrigins', [])
        require(isinstance(origins,list), 'allowedOrigins must be an array')
        seen = set()
        for raw in origins if isinstance(origins,list) else []:
            try:
                item = origin(raw, exact=True)
                require(item not in seen, 'Duplicate allowed origin')
                seen.add(item)
            except ValueError as exc: errors.append(str(exc))
        return errors
    if web is None: return errors
    require(isinstance(web, dict), 'runtime.web must be an object')
    if not isinstance(web,dict): return errors
    require(version(manifest.get('minCanEngineVersion')) >= (1,8,0), 'runtime.web requires CanEngine 1.8.0+')
    executable = web.get('executable','')
    native = web.get('nativeTargets', [])
    require(isinstance(native, list), 'nativeTargets must be an array')
    if native:
        require(not executable and not web.get('pythonAdapter') and not web.get('pythonPath') and not runtime.get('requirements') and not manifest.get('commands'), 'Native variants cannot have a default executable, Python adapter or extra runtime')
        seen = set()
        for target in native if isinstance(native,list) else []:
            require(isinstance(target,dict), 'nativeTargets entries must be objects')
            if not isinstance(target,dict): continue
            require(set(target) <= {'os','arch','executable'}, 'Unknown nativeTargets field')
            pair = (target.get('os'), target.get('arch'))
            valid_pair = all(isinstance(p,str) for p in pair) and pair in {('darwin','arm64'), ('darwin','amd64'), ('windows','amd64')}
            require(valid_pair, 'Unsupported native target')
            if not valid_pair: continue
            require(pair not in seen, 'Duplicate native target')
            seen.add(pair)
            raw = target.get('executable','')
            prefix = 'backend/' + pair[0] + '-' + pair[1] + '/'
            safe = isinstance(raw,str) and raw.startswith(prefix) and len(raw)>len(prefix) and not any(c in raw for c in '\\:\x00\r\n') and '..' not in PurePosixPath(raw).parts and str(PurePosixPath(raw)) == raw
            require(safe, 'Native executable must be a safe path under its backend/<os>-<arch>/ directory')
            if safe:
                actual = root/raw
                require(actual.is_file() and not actual.is_symlink() and actual.resolve().is_relative_to(root), 'Missing or unsafe native executable: ' + raw)
        platforms = manifest.get('platforms') or []
        declared = [(p.get('os'),p.get('arch')) for p in platforms if isinstance(p,dict)] if isinstance(platforms,list) else []
        require(isinstance(platforms,list) and len(platforms)==len(declared)==len(seen) and all(all(isinstance(part,str) for part in pair) for pair in declared) and len(set(declared))==len(declared) and set(declared)==seen, 'platforms must exactly match nativeTargets')
    else:
        require(isinstance(executable,str) and bool(executable.strip()) and not any(c in executable for c in ('\x00','\r','\n')), 'Missing or invalid Web executable')
        if isinstance(executable,str):
            require(not Path(executable).is_absolute() and '\\' not in executable and '..' not in Path(executable).parts, 'Web executable must be a runtime tool or safe bundle path')
    require(isinstance(web.get('args',[]),list) and all(isinstance(x,str) and '\x00' not in x for x in web.get('args',[])), 'Web args must be a string array')
    require(web.get('pythonAdapter','') in ('','http-server'), 'Unknown pythonAdapter')
    network = web.get('network','loopback')
    require(network in ('','loopback','internet'), 'Unknown Web network mode')
    if network == 'internet': require('web.network' in manifest.get('permissions',[]), 'Internet Web backend needs web.network')
    timeout = web.get('startupTimeoutMs',0)
    require(isinstance(timeout,int) and 0 <= timeout <= 60000, 'Web startup timeout must be 0-60000 ms')
    for key in ('entryPath','readyPath'):
        raw = web.get(key,'')
        if raw:
            u = urlsplit(raw)
            require(raw.startswith('/') and not raw.startswith('//') and not u.scheme and not u.netloc and not u.fragment and '\\' not in raw and not raw.startswith('/__canengine__/') and '__canengine_launch' not in u.query, 'Invalid or reserved Web '+key)
    for raw in [*web.get('pythonPath',[]), *([web['workingDir']] if web.get('workingDir') not in (None,'','.') else [])]:
        p = Path(raw)
        require(bool(raw) and not p.is_absolute() and '..' not in p.parts and '\\' not in raw and ':' not in raw and (root/p).is_dir() and (root/p).resolve().is_relative_to(root), 'Missing/unsafe Web directory: '+str(raw))
    ids = set()
    for directory in web.get('dataDirectories',[]):
        identity = directory.get('id','')
        require(bool(re.fullmatch(r'[a-z][a-z0-9_]{0,31}',identity)) and identity not in ids, 'Invalid or duplicate Web data directory id')
        ids.add(identity)
        require(bool(directory.get('label','').strip()), 'Web data directory needs a label')
        access = directory.get('access')
        require(access in ('read','read-write'), 'Invalid Web directory access')
        needed = 'web.files.write' if access == 'read-write' else 'web.files.read'
        require(needed in manifest.get('permissions',[]), 'Web directory needs '+needed)
    if (web.get('setup') or {}).get('deferred'):
        require(network != 'internet' and all(d.get('access') == 'read' for d in web.get('dataDirectories',[])), 'Deferred setup supports loopback with read-only directories')
    return errors
