#!/usr/bin/env python3
"""Generate a self-contained CEAPP source project with least-privilege profiles."""
import argparse
import json
from pathlib import Path
import re
import shutil

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
    'full': ['overview', 'files', 'jobs', 'runtime', 'ai', 'data', 'phone', 'system', 'diagnostics']
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
        'nameI18n': {'zh-CN': name, 'en-US': name}, 'version': '1.0.0',
        'description': 'CanEngine public bridge demonstration: ' + profile,
        'descriptionI18n': {'zh-CN': 'CanEngine \u6865\u63a5\u6f14\u793a', 'en-US':'CanEngine public bridge demonstration'},
        'entry':'index.html', 'icon':'assets/logo.png', 'minCanEngineVersion':'1.7.3',
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

def generate(output: Path, app_id: str, name: str, profile: str, datasets=(), actions=()):
    manifest, config = settings(app_id,name,profile,datasets,actions)
    output=output.resolve()
    if output.exists():
        raise ValueError('Destination already exists; use a new directory to protect existing work')
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
    args=parser.parse_args()
    try: print(generate(args.output,args.app_id,args.name,args.profile,args.dataset,args.action))
    except (OSError,ValueError) as exc: parser.exit(1,str(exc)+'\n')
