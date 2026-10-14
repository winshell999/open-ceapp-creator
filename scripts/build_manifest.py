"""Authoring-only Python build contract. Native compilation is a separate gate."""
from pathlib import Path, PurePosixPath
import re


def validate_build(config, manifest, root: Path):
    errors = []
    root = root.resolve()

    def require(condition, message):
        if not condition:
            errors.append(message)

    def fields(value, allowed, label):
        if not isinstance(value, dict):
            errors.append(label + ' must be an object')
            return {}
        require(set(value) <= set(allowed), label + ' has unknown fields')
        return value

    def local(value, directory=False):
        if not isinstance(value, str) or not value or value in ('.', '..') or any(c in value for c in '\\:\x00\r\n'):
            errors.append('Invalid build path: ' + repr(value))
            return False
        relative = PurePosixPath(value)
        if relative.is_absolute() or '..' in relative.parts or str(relative) != value:
            errors.append('Unsafe build path: ' + value)
            return False
        actual = root / value
        if not actual.resolve().is_relative_to(root) or actual.is_symlink():
            errors.append('Build path escapes project or is a symlink: ' + value)
            return False
        require(actual.is_dir() if directory else actual.is_file() or actual.is_dir(), 'Missing build path: ' + value)
        return actual.exists()

    config = fields(config, ('schemaVersion', 'python', 'assets', 'targets'), 'ceapp.build.json')
    require(type(config.get('schemaVersion')) is int and config['schemaVersion'] == 1, 'Build schemaVersion must be 1')
    python = fields(config.get('python'), ('entry', 'sourcePaths', 'includePackages', 'outputName'), 'build.python')
    entry = python.get('entry', '')
    require(isinstance(entry, str) and entry.endswith('.py'), 'build.python.entry must be a .py file')
    if local(entry):
        require((root / entry).is_file(), 'Build entry must be a regular file')
    name = python.get('outputName', '')
    require(isinstance(name, str) and bool(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name)) and not name.lower().startswith('python'), 'Invalid build.python.outputName')
    for key in ('sourcePaths', 'includePackages'):
        values = python.get(key, [])
        require(isinstance(values, list), 'build.python.' + key + ' must be an array')
        for value in values if isinstance(values, list) else []:
            if key == 'sourcePaths':
                local(value, directory=True)
            else:
                require(isinstance(value, str) and bool(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*', value)), 'Invalid build Python package')
    assets = config.get('assets')
    require(isinstance(assets, list), 'Build assets must be an explicit array')
    for value in assets if isinstance(assets, list) else []:
        if local(value):
            require(value not in ('app.json', 'ceapp.build.json', 'ceapp.native.json', 'backend') and not value.startswith('backend/'), 'Reserved build asset: ' + value)
            actual = root / value
            for file in [actual] if actual.is_file() else actual.rglob('*'):
                if file.is_file():
                    require(not file.is_symlink() and file.resolve().is_relative_to(root), 'Symlink in build assets: ' + str(file.relative_to(root)))
                    require(file.suffix.lower() not in ('.py', '.pyc', '.pyo', '.pyx', '.pyi', '.c', '.cpp', '.h', '.pem', '.key'), 'Source or key in build assets: ' + str(file.relative_to(root)))
    targets = config.get('targets')
    require(isinstance(targets, list) and bool(targets), 'Build targets must be explicit')
    allowed = {('darwin', 'arm64'), ('darwin', 'amd64'), ('windows', 'amd64')}
    for value in targets if isinstance(targets, list) else []:
        value = fields(value, ('os', 'arch'), 'build.target')
        target = (value.get('os'), value.get('arch'))
        require(all(isinstance(part, str) for part in target) and target in allowed, 'Unsupported build target: ' + str(target))
        platforms = manifest.get('platforms') or []
        require(any(isinstance(p, dict) and p.get('os') in ('*', target[0]) and p.get('arch') in ('*', target[1]) for p in platforms), 'Build target not supported by manifest: ' + str(target))
    runtime = manifest.get('runtime') or {}
    web = runtime.get('web') or {}
    require(bool(web) and not runtime.get('remoteWeb') and not manifest.get('commands'), 'Build mode requires runtime.web and empty commands')
    executable = web.get('executable', '')
    args = web.get('args') or []
    require(isinstance(executable, str) and Path(executable).name.lower().startswith('python') and isinstance(args, list) and bool(args) and args[0] == entry and web.get('workingDir', '.') in ('', '.'), 'Build runtime must launch the configured Python entry from project root')
    require(all(r.get('id') in ('base-runtime', 'python-runtime') for r in runtime.get('requirements', []) if isinstance(r, dict)), 'Build mode supports only base/python runtime requirements')
    return errors
