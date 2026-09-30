"""Deterministic CLI and manifest tests. Does not call a native CanEngine host."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import create_ceapp
import validate_ceapp

class ProcessorTests(unittest.TestCase):
    def run_case(self,name,content,extra=(),success=True):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary); source=base/name;source.write_bytes(content)
            out=base/'output';result=out/'result.json'
            proc=subprocess.run([sys.executable,str(ROOT/'assets/starter/scripts/process_file.py'),'-i',str(source),'-o',str(out),'--result-json',str(result),*extra],capture_output=True,text=True,timeout=15)
            self.assertEqual(proc.returncode==0,success,proc.stderr)
            payload=json.loads(result.read_text());self.assertEqual(payload['ok'],success)
            self.assertFalse(list(out.glob('*.tmp')))
            if success:
                self.assertEqual(len(payload['files']),2)
                for file in payload['files']:
                    self.assertTrue(Path(file['path']).is_file());self.assertEqual(file['size'],Path(file['path']).stat().st_size)
                self.assertEqual(Path(payload['files'][0]['path']).read_bytes(),content)
            return payload
    def test_unicode_filename_and_text(self):self.run_case('\u6d4b\u8bd5 \u6587\u4ef6.txt','\u4e2d\u6587\nhello'.encode())
    def test_empty_text(self):self.run_case('empty.txt',b'')
    def test_csv(self):self.run_case('sample.csv',b'name,value\n"hello, world",5\n')
    def test_json(self):self.run_case('data.json',b'{"x":[1,2]}')
    def test_malformed_json(self):self.run_case('bad.json',b'{broken',success=False)
    def test_invalid_utf8(self):self.run_case('bad.txt',b'\xff\xfe\xfa',success=False)
    def test_binary_hash(self):self.run_case('asset.bin',bytes(range(256)))
    def test_bad_delay(self):self.run_case('a.txt',b'hi',extra=['--sleep','-1'],success=False)
    def test_sleep_fraction(self):self.run_case('a.txt',b'hi',extra=['--sleep','0.01'])
    def test_no_input(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t);p=subprocess.run([sys.executable,str(ROOT/'assets/starter/scripts/process_file.py'),'-o',t,'--result-json',str(out/'result.json')],capture_output=True)
            self.assertNotEqual(p.returncode,0);self.assertFalse(json.loads((out/'result.json').read_text())['ok'])
    def test_sequence(self):
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);a=base/'a.txt';b=base/'b.txt';a.write_text('a');b.write_text('b');out=base/'out'
            p=subprocess.run([sys.executable,str(ROOT/'assets/starter/scripts/process_file.py'),'--sequence',str(a),'--sequence',str(b),'-o',str(out),'--result-json',str(out/'result.json')],capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(len(json.loads((out/'result.json').read_text())['files']),3)
    def test_result_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'input.txt';f.write_text('original')
            p=subprocess.run([sys.executable,str(ROOT/'assets/starter/scripts/process_file.py'),'-i',str(f),'-o',t,'--result-json',str(f)],capture_output=True)
            self.assertNotEqual(p.returncode,0);self.assertEqual(f.read_text(),'original')

class GeneratorTests(unittest.TestCase):
    def test_nine_profiles_validate(self):
        with tempfile.TemporaryDirectory() as t:
            for profile in create_ceapp.PROFILES:
                with self.subTest(profile=profile):
                    root=create_ceapp.generate(Path(t)/profile,'demo-'+profile,profile,profile)
                    report=validate_ceapp.validate(root);self.assertTrue(report['ok'],report)
    def test_destination_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):create_ceapp.generate(Path(t),'demo','demo','minimal')
    def test_invalid_appid(self):
        with self.assertRaises(ValueError):create_ceapp.settings('../x','x','minimal')
    def test_unexpected_shared_ids_rejected(self):
        with self.assertRaises(ValueError):create_ceapp.settings('x','x','files',['dataset'])
    def test_wildcard_rejected(self):
        with self.assertRaises(ValueError):create_ceapp.settings('x','x','data',['*'])
    def test_exact_shared_ids_in_both_files(self):
        manifest,config=create_ceapp.settings('x','x','data',['authorized-dataset'],['authorized-action'])
        self.assertEqual(manifest['capabilities']['dataBridge']['datasets'],config['datasets'])
        self.assertIn('data.action',manifest['permissions'])
    def test_ai_text_profile_is_least_privilege(self):
        manifest,_=create_ceapp.settings('x','x','ai-text');self.assertEqual(manifest['permissions'],['ai.text.generate'])
    def test_default_has_no_shared_fake_ids(self):
        manifest,_=create_ceapp.settings('x','x','full');self.assertEqual(manifest['capabilities']['dataBridge']['datasets'],[])
    def test_corrupt_manifest_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','demo','demo','minimal');(p/'app.json').write_text('{}');self.assertFalse(validate_ceapp.validate(p)['ok'])
    def test_permission_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','demo','demo','ai-text');m=json.loads((p/'app.json').read_text());m['permissions']=[];(p/'app.json').write_text(json.dumps(m));self.assertFalse(validate_ceapp.validate(p)['ok'])
    def test_missing_asset_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','demo','demo','minimal');(p/'assets/logo.png').unlink();self.assertFalse(validate_ceapp.validate(p)['ok'])
    def test_cdn_injection_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','demo','demo','minimal');f=p/'index.html';f.write_text(f.read_text()+'<script src="https://cdn.example.com/x.js"></script>');self.assertFalse(validate_ceapp.validate(p)['ok'])
    def test_syntax_error_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','demo','demo','minimal');(p/'app.js').write_text('function {');self.assertFalse(validate_ceapp.validate(p)['ok'])

if __name__=='__main__':unittest.main(verbosity=2)
