"""Conservative authoring checks for the public runtime.web browser bridge.

These checks do not inspect a website or prove selector/native compatibility.
Errors deliberately omit URLs, selectors and field values.
"""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from web_manifest import version

PROFILE = 'form-prefill-v1'
PERMISSION = 'browser.form.prefill'
KEY = re.compile(r'[a-zA-Z][a-zA-Z0-9_-]{0,63}')
KINDS = {'text', 'search', 'email', 'tel', 'number', 'url', 'date',
         'datetime-local', 'time', 'month', 'week', 'textarea', 'select', 'checkbox', 'radio'}
KNOWN = {PROFILE: (PERMISSION, (1, 8, 0)),
         'mdac-registration-v1': ('browser.mdac.fill', (1, 8, 0))}


def identity(value):
    return isinstance(value, str) and KEY.fullmatch(value) is not None


def target_url(raw):
    """A fixed HTTPS page, never a data-bearing URL assembled at runtime."""
    if not isinstance(raw, str) or len(raw.encode('utf-8')) > 2048:
        raise ValueError('Browser target must be a fixed HTTPS page')
    if not raw.startswith('https://') or any(c.isspace() or c in '\x00\\*' for c in raw):
        raise ValueError('Browser target must be a fixed HTTPS page')
    try:
        url = urlsplit(raw)
        valid = (bool(url.hostname) and url.netloc == url.netloc.lower() and
                 url.username is None and url.password is None)
        _ = url.port
    except ValueError:
        valid = False
    if not valid:
        raise ValueError('Browser target must have a lowercase host without credentials or wildcards')
    return raw


def validate_browser(manifest):
    errors = []
    caps = manifest.get('capabilities') or {}
    browser = caps.get('browser') if isinstance(caps, dict) else None
    permissions = manifest.get('permissions') or []
    browser_permissions = [p for p in permissions if isinstance(p, str) and p.startswith('browser.')]
    if browser is None:
        return ['Browser permission requires its controlled profile'] if browser_permissions else []
    if not isinstance(browser, dict):
        return ['capabilities.browser must be an object']
    if set(browser) - {'profiles', 'targets'}:
        errors.append('Unknown browser declaration; no arbitrary automation capability')
    runtime = manifest.get('runtime') or {}
    if not isinstance(runtime.get('web'), dict) or runtime.get('remoteWeb') is not None:
        errors.append('Browser prefill requires the local runtime.web bridge')
    profiles = browser.get('profiles')
    if (not isinstance(profiles, list) or not 1 <= len(profiles) <= 2 or
            not all(isinstance(p, str) and p in KNOWN for p in profiles) or
            len(set(profiles)) != len(profiles)):
        return errors + ['Invalid or duplicate controlled browser profile']
    for profile in profiles:
        permission, minimum = KNOWN[profile]
        if permission not in permissions:
            errors.append('Browser profile requires its matching permission')
        if version(manifest.get('minCanEngineVersion')) < minimum:
            errors.append('Browser profile requires the matching minimum host version')
    if any(p not in {KNOWN[s][0] for s in profiles} for p in browser_permissions):
        errors.append('Unknown or mismatched browser permission')
    targets = browser.get('targets', [])
    if PROFILE not in profiles:
        if targets:
            errors.append('Fixed targets require form-prefill-v1')
        return errors
    if not isinstance(targets, list) or not 1 <= len(targets) <= 16:
        return errors + ['Generic prefill needs 1–16 declared page targets']
    seen = set()
    for target in targets:
        if not isinstance(target, dict) or set(target) != {'id', 'url'}:
            errors.append('Browser target must contain only id and url')
            continue
        name = target['id']
        if not identity(name) or name in seen:
            errors.append('Invalid or duplicate browser target ID')
        if identity(name):
            seen.add(name)
        try:
            target_url(target['url'])
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def selector(value):
    return (isinstance(value, str) and bool(value.strip()) and
            len(value.encode('utf-8')) <= 512 and not any(c in value for c in '\x00\r\n'))


def validate_request(request, targets=None):
    """Validate public JSON shape, size and dependency DAG; never echo payload."""
    errors = []
    if not isinstance(request, dict) or set(request) != {'schemaVersion', 'target', 'scope', 'fields'}:
        return ['Prefill request must contain only schemaVersion, target, scope and fields']
    try:
        size = len(json.dumps(request, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8'))
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return ['Prefill request is not valid JSON']
    if size > 65536:
        errors.append('Prefill request exceeds 64 KiB')
    if type(request['schemaVersion']) is not int or request['schemaVersion'] != 1:
        errors.append('Prefill schemaVersion must be 1')
    if not identity(request['target']) or (targets is not None and request['target'] not in targets):
        errors.append('Prefill target must reference this app’s declared target')
    if not selector(request['scope']):
        errors.append('Prefill scope must be a bounded CSS selector')
    fields = request['fields']
    if not isinstance(fields, list) or not 1 <= len(fields) <= 64:
        return errors + ['Prefill needs 1–64 fields']
    graph = {}
    for index, field in enumerate(fields):
        prefix = 'Prefill field ' + str(index + 1) + ': '
        if (not isinstance(field, dict) or
                not {'key', 'selector', 'kind', 'value'} <= set(field) or
                set(field) - {'key', 'selector', 'kind', 'value', 'match', 'events', 'dependsOn'}):
            errors.append(prefix + 'invalid fields or unknown scripting property')
            continue
        key = field['key']
        if not identity(key) or key in graph:
            errors.append(prefix + 'invalid or duplicate key')
        if not selector(field['selector']):
            errors.append(prefix + 'invalid selector')
        kind = field['kind']
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(prefix + 'unsupported native control kind')
        match = field.get('match', '')
        if match not in ('', 'exact', 'case-insensitive'):
            errors.append(prefix + 'invalid readback match rule')
        value = field['value']
        if kind in ('checkbox', 'radio'):
            if type(value) is not bool or match == 'case-insensitive':
                errors.append(prefix + 'toggle needs a boolean and exact matching')
        elif not isinstance(value, str) or len(value.encode('utf-8')) > 8192 or '\x00' in value:
            errors.append(prefix + 'value must be a string up to 8 KiB without NUL')
        events = field.get('events', [])
        if (not isinstance(events, list) or
                not all(isinstance(e, str) and e in ('input', 'change', 'blur') for e in events) or
                len(set(events)) != len(events)):
            errors.append(prefix + 'only unique input/change/blur events are allowed')
        deps = field.get('dependsOn', [])
        if (not isinstance(deps, list) or len(deps) > 16 or
                not all(identity(d) for d in deps) or len(set(deps)) != len(deps)):
            errors.append(prefix + 'invalid dependencies')
            deps = []
        if identity(key):
            graph[key] = deps
    if any(d not in graph or d == key for key, deps in graph.items() for d in deps):
        errors.append('Prefill has unknown or self dependencies')
    remaining = set(graph)
    done = set()
    while remaining:
        ready = {key for key in remaining if set(graph[key]) <= done}
        if not ready:
            errors.append('Prefill dependencies contain a cycle or missing key')
            break
        done.update(ready)
        remaining -= ready
    return errors


def read_request(path: Path):
    raw = path.read_bytes()
    if len(raw) > 65536:
        raise ValueError('Mapping fixture exceeds 64 KiB')
    try:
        request = json.loads(raw)
        issues = validate_request(request)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ValueError('Mapping fixture is invalid JSON') from None
    if issues:
        raise ValueError('; '.join(issues))
    return request
