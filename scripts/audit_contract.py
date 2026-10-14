#!/usr/bin/env python3
"""Check literal public bridge method names against the inspected source inventory.
Dynamic factories/prefixes still require review and domain tests; this is not a JS typechecker.
"""
import argparse
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PATTERN=re.compile(r'\b(?:client|c|this(?:\.client)?)\.(?:call|mutate|raw|has|subscribe)\(\s*([\'\"])([^\'\"]+)\1\s*[,)]')
WEB_BROWSER=re.compile(r'\b(?:window\.CanEngine|host)\.browser\.([A-Za-z][A-Za-z0-9_]*)\s*\(')

def audit(path: Path):
    spec=json.loads((ROOT/'references/bridge-methods.json').read_text())
    allowed={entry['method'] for entry in spec['methods']}
    checked=[];errors=[]
    for file in path.rglob('*.js'):
        source=file.read_text(encoding='utf-8')
        for match in PATTERN.finditer(source):
            method=match.group(2)
            if method not in allowed:errors.append({'file':file.relative_to(path).as_posix(),'method':method})
            checked.append(method)
        for match in WEB_BROWSER.finditer(source):
            method='browser.'+match.group(1)
            if method not in allowed:errors.append({'file':file.relative_to(path).as_posix(),'method':method})
            checked.append(method)
    return {'ok':not errors,'literalMethodsChecked':sorted(set(checked)),'unknownMethods':errors,
            'limitation':'Dynamic call paths, runtime surface, permissions and request/response shapes need separate review/tests.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);args=p.parse_args()
    result=audit(args.path);print(json.dumps(result,indent=2));raise SystemExit(0 if result['ok'] else 1)
