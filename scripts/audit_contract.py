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

def audit(path: Path):
    spec=json.loads((ROOT/'references/bridge-methods.json').read_text())
    allowed={entry['method'] for entry in spec['methods']}
    checked=[];errors=[]
    for file in path.rglob('*.js'):
        for match in PATTERN.finditer(file.read_text(encoding='utf-8')):
            method=match.group(2)
            if method not in allowed:errors.append({'file':file.relative_to(path).as_posix(),'method':method})
            checked.append(method)
    return {'ok':not errors,'literalMethodsChecked':sorted(set(checked)),'unknownMethods':errors,
            'limitation':'Dynamic call paths and request/response shapes need separate review/tests.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);args=p.parse_args()
    result=audit(args.path);print(json.dumps(result,indent=2));raise SystemExit(0 if result['ok'] else 1)
