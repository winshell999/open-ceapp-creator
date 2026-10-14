"""Public prefill contract, generation and real local HTTP gates; no native host."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import audit_contract
import browser_prefill as contract
import create_ceapp
import validate_ceapp

FIXTURE = {
    'schemaVersion':1, 'target':'contact', 'scope':'form#contact',
    'fields':[
        {'key':'name', 'selector':'#name', 'kind':'text', 'value':'TEST USER'},
        {'key':'country', 'selector':'#country', 'kind':'select', 'value':'SGP', 'events':['change']},
        {'key':'city', 'selector':'#city', 'kind':'select', 'value':'SG', 'dependsOn':['country']},
    ],
}


class RequestTests(unittest.TestCase):
    def test_valid_dependency_request_and_toggle(self):
        request = copy.deepcopy(FIXTURE)
        request['fields'].append({'key':'businessFlag', 'selector':'#flag', 'kind':'checkbox', 'value':False})
        self.assertEqual(contract.validate_request(request, {'contact'}), [])

    def test_reject_unsafe_and_invalid_shapes(self):
        changes = [
            lambda r:r.update(schemaVersion=True), lambda r:r.update(url='https://other.example'),
            lambda r:r.update(target='other'), lambda r:r.update(scope=''),
            lambda r:r.update(fields=[]), lambda r:r.update(fields=r['fields']*22),
            lambda r:r['fields'][0].update(kind='password'), lambda r:r['fields'][0].update(kind='hidden'),
            lambda r:r['fields'][0].update(kind='file'), lambda r:r['fields'][0].update(kind='submit'),
            lambda r:r['fields'][0].update(script='alert(1)'), lambda r:r['fields'][0].update(value=123),
            lambda r:r['fields'][0].update(value='\x00'), lambda r:r['fields'][0].update(value='中'*2731),
            lambda r:r['fields'][0].update(selector='中'*171), lambda r:r['fields'][0].update(selector='#x\n'),
            lambda r:r['fields'][0].update(events=['click']), lambda r:r['fields'][0].update(events=['submit']),
            lambda r:r['fields'][0].update(events=['change','change']),
            lambda r:r['fields'][0].update(kind='checkbox',value='false'),
            lambda r:r['fields'][0].update(kind='radio',value=True,match='case-insensitive'),
            lambda r:r['fields'][0].update(dependsOn=['missing']),
            lambda r:(r['fields'][0].update(dependsOn=['city']),r['fields'][1].update(dependsOn=['name'])),
            lambda r:r['fields'][1].update(dependsOn=['city']),
            lambda r:r['fields'][2].update(dependsOn=['country','country']),
            lambda r:r['fields'][2].update(dependsOn=['city']),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                request = copy.deepcopy(FIXTURE); change(request)
                self.assertTrue(contract.validate_request(request, {'contact'}))

    def test_size_bounds_and_redacted_errors(self):
        request = copy.deepcopy(FIXTURE)
        request['fields'][0]['value'] = 'PRIVATE-FIXTURE-SENTINEL'*4000
        report = contract.validate_request(request)
        self.assertTrue(report)
        self.assertNotIn('PRIVATE-FIXTURE-SENTINEL', json.dumps(report))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'bad.json'; path.write_text(json.dumps(request))
            with self.assertRaisesRegex(ValueError, '64 KiB'):
                contract.read_request(path)


class GeneratorTests(unittest.TestCase):
    def generate(self, output):
        return create_ceapp.generate(output, 'contact-prefill', 'Contact Prefill', 'form-prefill',
                                     url='https://forms.example.com/contact', mapping=copy.deepcopy(FIXTURE))

    def test_generated_source_has_narrow_permissions_and_versions(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.generate(Path(temporary)/'app')
            manifest = json.loads((path/'app.json').read_text())
            self.assertEqual(manifest['version'], '1.8.0')
            self.assertEqual(manifest['minCanEngineVersion'], '1.8.0')
            self.assertEqual(manifest['permissions'], ['browser.form.prefill'])
            self.assertEqual(manifest['runtime']['web']['network'], 'loopback')
            self.assertNotIn('remoteWeb', manifest['runtime'])
            self.assertEqual(manifest['commands'], {})
            report = validate_ceapp.validate(path)
            self.assertTrue(report['ok'], report)
            self.assertIn('prefill-request-structure', report['checks'])

    def test_mapping_required_and_rejections_do_not_create_output(self):
        cases = [{'mapping':None}, {'url':'http://127.0.0.1/form'}, {'url':'https://user:secret@example.com/'},
                 {'url':'https://*.example.com/'}, {'url':'https://EXAMPLE.com/'},
                 {'allowed_origins':['https://other.example']}, {'compile_python':True}]
        with tempfile.TemporaryDirectory() as temporary:
            for index, case in enumerate(cases):
                args = {'url':'https://example.com/form', 'mapping':copy.deepcopy(FIXTURE)}; args.update(case)
                output = Path(temporary)/str(index)
                with self.assertRaises(ValueError):
                    create_ceapp.generate(output, 'prefill', 'Prefill', 'form-prefill', **args)
                self.assertFalse(output.exists())

    def test_public_manifest_permissions_and_targets(self):
        changes = [lambda m:m.update(permissions=[]), lambda m:m.update(permissions=['browser.*']),
                   lambda m:m.update(minCanEngineVersion='1.7.10'),
                   lambda m:m['runtime'].pop('web'), lambda m:m['runtime'].update(remoteWeb={'url':'https://example.com/'}),
                   lambda m:m['capabilities']['browser'].update(profiles=['uncontrolled']),
                   lambda m:m['capabilities']['browser'].update(targets=[]),
                   lambda m:m['capabilities']['browser']['targets'].append(m['capabilities']['browser']['targets'][0]),
                   lambda m:m['capabilities']['browser']['targets'][0].update(url='https://secret@example.com/'),
                   lambda m:m['capabilities']['browser']['targets'][0].update(url='https://example.com/\n'),
                   lambda m:m['capabilities']['browser'].update(evaluate=True)]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.generate(Path(temporary)/'app')
            manifest = json.loads((path/'app.json').read_text())
            for change in changes:
                current = copy.deepcopy(manifest); change(current)
                self.assertTrue(contract.validate_browser(current))

    def test_config_cannot_reference_another_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.generate(Path(temporary)/'app')
            config_path = path/'assets/form-config.json'
            config = json.loads(config_path.read_text()); config['request']['target'] = 'other'
            config_path.write_text(json.dumps(config))
            self.assertFalse(validate_ceapp.validate(path)['ok'])

    def test_cli_and_literal_browser_audit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); mapping = root/'request.json'; mapping.write_text(json.dumps(FIXTURE))
            process = subprocess.run([sys.executable, str(ROOT/'scripts/create_ceapp.py'), '--profile','form-prefill',
                                      '--app-id','cli-prefill','--name','CLI','--url','https://example.com/form',
                                      '--mapping',str(mapping),'--output',str(root/'app')], capture_output=True, text=True, timeout=20)
            self.assertEqual(process.returncode, 0, process.stderr)
            audit = audit_contract.audit(root/'app'); self.assertTrue(audit['ok'])
            self.assertIn('browser.prefill', audit['literalMethodsChecked'])
            (root/'app/assets/bad.js').write_text('host.browser.evaluate("unsafe")')
            self.assertFalse(audit_contract.audit(root/'app')['ok'])

    def test_real_http_static_allowlist_and_no_value_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = self.generate(Path(temporary)/'app')
            spec = importlib.util.spec_from_file_location('prefill_http_fixture', path/'server.py')
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            server = module.ThreadingHTTPServer(('127.0.0.1',0), module.Handler)
            thread = threading.Thread(target=lambda:server.serve_forever(poll_interval=.05), daemon=True)
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                thread.start()
                base = 'http://127.0.0.1:'+str(server.server_port)
                try:
                    for route in ['/','/health','/assets/app.js','/assets/ceapp-i18n.js','/assets/styles.css','/assets/form-config.json','/assets/icon.svg']:
                        with urlopen(base+route,timeout=3) as response:
                            self.assertEqual(response.status,200)
                            self.assertEqual(response.headers['Cache-Control'],'private, no-store')
                            self.assertTrue(response.read())
                    for route in ['/app.json','/../server.py','/?name=PRIVATE-FIXTURE-SENTINEL']:
                        with self.assertRaises(HTTPError) as caught: urlopen(base+route, timeout=3)
                        self.assertEqual(caught.exception.code,404)
                        self.assertNotIn(b'PRIVATE-FIXTURE-SENTINEL',caught.exception.read())
                        caught.exception.close()
                    with self.assertRaises(HTTPError) as caught:
                        urlopen(Request(base+'/',data=b'PRIVATE-FIXTURE-SENTINEL',method='POST'),timeout=3)
                    self.assertEqual(caught.exception.code,405)
                    self.assertNotIn(b'PRIVATE-FIXTURE-SENTINEL',caught.exception.read())
                    caught.exception.close()
                finally:
                    server.shutdown(); server.server_close(); thread.join(timeout=2)
            self.assertEqual(stderr.getvalue(),'')


if __name__ == '__main__':
    unittest.main(verbosity=2)
