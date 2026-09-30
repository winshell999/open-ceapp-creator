#!/usr/bin/env python3
"""Host-managed file processing. Standard library only; never executes input files."""
import argparse
import csv
import hashlib
import io
import json
import mimetypes
import os
from pathlib import Path
import shutil
import sys
import time

MAX_TEXT_BYTES = 16 * 1024 * 1024

def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)

def file_result(path: Path) -> dict:
    return {'name': path.name, 'path': str(path.resolve()), 'type': 'file',
            'mime': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
            'size': path.stat().st_size}

def inspect(path: Path) -> dict:
    if not path.is_file():
        raise ValueError('Input is not a regular file: ' + path.name)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    record = {'name': path.name, 'size': path.stat().st_size, 'sha256': digest.hexdigest()}
    if path.suffix.lower() in {'.txt', '.csv', '.json'}:
        if record['size'] > MAX_TEXT_BYTES:
            raise ValueError('Text input exceeds the 16 MiB demo limit')
        text = path.read_text(encoding='utf-8-sig')
        if path.suffix.lower() == '.json':
            data = json.loads(text)
            record.update(kind='json', topLevelType=type(data).__name__,
                          items=len(data) if isinstance(data, (list, dict)) else 1)
        elif path.suffix.lower() == '.csv':
            rows = list(csv.reader(io.StringIO(text, newline='')))
            record.update(kind='csv', rows=max(0, len(rows) - 1), columns=rows[0] if rows else [])
        else:
            record.update(kind='text', lines=len(text.splitlines()), characters=len(text))
    else:
        record['kind'] = 'binary'
    return record

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', '--input')
    parser.add_argument('--sequence', action='append', default=[])
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--result-json', required=True)
    parser.add_argument('--sleep', type=float, default=0)
    args = parser.parse_args(argv)
    started = time.monotonic()
    output = Path(args.output).resolve()
    result_path = Path(args.result_json).resolve()
    try:
        if not 0 <= args.sleep <= 10:
            raise ValueError('sleep must be between 0 and 10 seconds')
        paths = [Path(p).resolve() for p in ([args.input] if args.input else []) + args.sequence]
        if not paths:
            raise ValueError('Choose at least one input file')
        if len(paths) > 12:
            raise ValueError('At most 12 files in the demonstration')
        if result_path in paths:
            raise ValueError('Result path must not overwrite an input')
        result_path.relative_to(output)
        output.mkdir(parents=True, exist_ok=True)
        for second in range(int(args.sleep)):
            print('progress: %d/%d' % (second, int(args.sleep)), flush=True)
            time.sleep(1)
        time.sleep(args.sleep - int(args.sleep))
        records, files = [], []
        for index, path in enumerate(paths, 1):
            print('inspecting: ' + path.name, flush=True)
            records.append(inspect(path))
            copied = output / ('copy-%02d-' % index + path.name)
            if copied == path:
                raise ValueError('Output must differ from input')
            shutil.copyfile(path, copied)
            files.append(file_result(copied))
        summary = output / 'inspection.json'
        atomic_json(summary, {'files': records})
        files.append(file_result(summary))
        atomic_json(result_path, {'ok': True, 'status': 'success', 'files': files, 'warnings': [],
                                 'durationMs': int((time.monotonic() - started) * 1000)})
        print('completed: %d input(s)' % len(records), flush=True)
        return 0
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        message = str(exc)[:1200]
        # Keep a machine-readable failure when the host output directory is writable.
        try:
            result_path.relative_to(output)
            if result_path not in [Path(p).resolve() for p in ([args.input] if args.input else []) + args.sequence]:
                atomic_json(result_path, {'ok': False, 'status': 'failed', 'files': [], 'warnings': [],
                                         'error': message, 'durationMs': int((time.monotonic()-started)*1000)})
        except (OSError, ValueError):
            pass
        print('processing failed: ' + message, file=sys.stderr, flush=True)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
