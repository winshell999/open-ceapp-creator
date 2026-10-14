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
    def native_release(self, root):
        p=create_ceapp.generate(root,'native-demo','Native demo','web-python')
        manifest=json.loads((p/'app.json').read_text())
        manifest['entry']='index.html'
        manifest['platforms']=[{'os':'darwin','arch':'arm64'},{'os':'windows','arch':'amd64'}]
        manifest['runtime']['requirements']=[]
        web=manifest['runtime']['web']
        web.pop('executable',None);web.pop('pythonAdapter',None);web['args']=[]
        web['nativeTargets']=[{**target,'executable':'backend/'+target['os']+'-'+target['arch']+'/server'+('.exe' if target['os']=='windows' else '')} for target in manifest['platforms']]
        for target in web['nativeTargets']:
            file=p/target['executable'];file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(b'structural fixture only')
        (p/'server.py').unlink()
        (p/'app.json').write_text(json.dumps(manifest))
        return p,manifest

    def test_native_variants_release_validates_without_default_executable(self):
        with tempfile.TemporaryDirectory() as t:
            p,m=self.native_release(Path(t)/'p')
            report=validate_ceapp.validate(p)
            self.assertTrue(report['ok'],report)
            self.assertEqual(m['minCanEngineVersion'],'1.8.0')

    def test_native_variants_reject_bad_platform_and_entry_mappings(self):
        changes=[lambda m:m['runtime']['web'].update(executable='backend/server'),lambda m:m['runtime']['web']['nativeTargets'][1].update(executable='backend/darwin-arm64/server'),lambda m:m['runtime']['web']['nativeTargets'][1].update(executable='backend/windows-amd64/../server.exe'),lambda m:m['platforms'].append(m['platforms'][0]),lambda m:m['runtime']['web']['nativeTargets'].append(m['runtime']['web']['nativeTargets'][0]),lambda m:m['runtime']['web']['nativeTargets'][1].update(arch='arm64'),lambda m:m['runtime']['web']['nativeTargets'][1].update(executable='backend/windows-amd64/missing.exe'),lambda m:m['runtime'].update(requirements=[{'id':'base-runtime'}]),lambda m:m['platforms'][1].update(arch=[])]
        with tempfile.TemporaryDirectory() as t:
            for index,change in enumerate(changes):
                p,m=self.native_release(Path(t)/str(index));change(m)
                (p/'app.json').write_text(json.dumps(m))
                self.assertFalse(validate_ceapp.validate(p)['ok'],m)

    def test_compiled_web_source_validates_and_preserves_versions(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','compiled','Compiled','web-python',compile_python=True)
            m=json.loads((p/'app.json').read_text())
            build=json.loads((p/'ceapp.build.json').read_text())
            self.assertEqual(m['version'],'1.8.0')
            self.assertEqual(m['minCanEngineVersion'],'1.8.0')
            self.assertEqual(m['runtime']['web']['args'],['server.py'])
            self.assertEqual(build['targets'][-1],{'os':'windows','arch':'amd64'})
            self.assertTrue((p/'server.py').is_file())
            self.assertTrue(validate_ceapp.validate(p)['ok'])

    def test_compilation_is_not_enabled_for_jobs_or_remote_web(self):
        with tempfile.TemporaryDirectory() as t:
            for profile in ('python','remote-web'):
                with self.assertRaises(ValueError):
                    create_ceapp.generate(Path(t)/profile,'compiled','Compiled',profile,url='https://example.com/',compile_python=True)
                self.assertFalse((Path(t)/profile).exists())

    def test_unsafe_or_leaking_build_config_fails(self):
        changes=[lambda b:b.update(assets=['../outside']),lambda b:b.update(assets=['server.py']),lambda b:b['python'].update(outputName='python3'),lambda b:b.update(targets=[{'os':'windows','arch':'arm64'}]),lambda b:b.update(unknown=True)]
        with tempfile.TemporaryDirectory() as t:
            for index,change in enumerate(changes):
                p=create_ceapp.generate(Path(t)/str(index),'compiled','Compiled','web-python',compile_python=True)
                b=json.loads((p/'ceapp.build.json').read_text());change(b)
                (p/'ceapp.build.json').write_text(json.dumps(b))
                self.assertFalse(validate_ceapp.validate(p)['ok'],b)

    def test_all_profiles_validate(self):
        with tempfile.TemporaryDirectory() as t:
            for profile in create_ceapp.PROFILES:
                with self.subTest(profile=profile):
                    mapping={'schemaVersion':1,'target':'test','scope':'form#fixture','fields':[{'key':'name','selector':'#name','kind':'text','value':'TEST USER'}]} if profile=='form-prefill' else None
                    root=create_ceapp.generate(Path(t)/profile,'demo-'+profile,profile,profile,url='https://example.com/',mapping=mapping)
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

    def test_remote_requires_explicit_url(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError): create_ceapp.generate(Path(t)/'p','remote','Remote','remote-web')
            self.assertFalse((Path(t)/'p').exists())

    def test_remote_is_manifest_only(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','remote','Remote','remote-web',url='https://example.com/app/')
            m=json.loads((p/'app.json').read_text())
            self.assertNotIn('entry',m);self.assertNotIn('commands',m)
            self.assertFalse((p/'index.html').exists());self.assertFalse((p/'app-config.js').exists())
            self.assertEqual(m['permissions'],['web.network'])
            self.assertEqual(m['minCanEngineVersion'],'1.8.0')
            self.assertNotIn('authorization',m['runtime']['remoteWeb'])

    def test_protected_remote_is_manifest_only_and_preserves_default_version(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','protected-demo','Protected','remote-web',url='https://example.com/app/index.php/',authorization='canengine')
            m=json.loads((p/'app.json').read_text())
            self.assertEqual(m['runtime']['remoteWeb']['authorization'],'canengine')
            self.assertEqual(m['version'],'1.8.0')
            self.assertEqual(m['minCanEngineVersion'],'1.8.0')
            self.assertEqual(m['permissions'],['web.network'])
            self.assertNotIn('commands',m)
            self.assertFalse(list(p.rglob('*.php')))
            self.assertFalse((p/'index.html').exists())
            report=validate_ceapp.validate(p)
            self.assertTrue(report['ok'],report)
            self.assertIn('remote-web-authorization-manifest',report['checks'])
            m['version']='1.6.4'
            (p/'app.json').write_text(json.dumps(m))
            self.assertTrue(validate_ceapp.validate(p)['ok'])
            self.assertEqual(json.loads((p/'app.json').read_text())['version'],'1.6.4')

    def test_protected_remote_cli(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'p'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/create_ceapp.py'),'--profile','remote-web','--authorization','canengine','--app-id','protected-demo','--name','Protected','--url','https://example.com/app/index.php/','--output',str(p)],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(validate_ceapp.validate(p)['ok'])
            self.assertEqual(json.loads((p/'app.json').read_text())['runtime']['remoteWeb']['authorization'],'canengine')

    def test_authorization_invalid_provider_or_profile_refused_before_writing(self):
        with tempfile.TemporaryDirectory() as t:
            for profile,provider in [('remote-web','unknown'),('web-python','canengine'),('minimal','canengine'),('form-prefill','canengine')]:
                with self.subTest(profile=profile,provider=provider):
                    p=Path(t)/profile
                    with self.assertRaises(ValueError):
                        create_ceapp.generate(p,'protected-demo','Protected',profile,url='https://example.com/',authorization=provider)
                    self.assertFalse(p.exists())

    def test_protected_manifest_rejects_invalid_auth_and_credentials_without_echo(self):
        marker='SYNTHETIC_SERVER_ONLY_VALUE'
        changes=[lambda m:m['runtime']['remoteWeb'].update(authorization='unknown'),lambda m:m['runtime']['remoteWeb'].update(authorization=True),lambda m:m['runtime']['remoteWeb'].update(authorization=None),lambda m:m.update(minCanEngineVersion='1.7.9'),lambda m:m['runtime']['remoteWeb'].update(appKey=marker),lambda m:m.update(licenseToken=marker),lambda m:m['runtime']['remoteWeb'].update(url='https://example.com/app/?ticket='+marker),lambda m:m['runtime']['remoteWeb'].update(url='https://example.com/app/#'+marker),lambda m:m['runtime']['remoteWeb'].update(url='https://example.com'),lambda m:m.update(appId='x'),lambda m:m['runtime']['remoteWeb'].update(authorizationEndpoint='entry')]
        with tempfile.TemporaryDirectory() as t:
            for index,change in enumerate(changes):
                p=create_ceapp.generate(Path(t)/str(index),'protected-demo','Protected','remote-web',url='https://example.com/app/',authorization='canengine')
                m=json.loads((p/'app.json').read_text());change(m)
                (p/'app.json').write_text(json.dumps(m))
                report=validate_ceapp.validate(p)
                self.assertFalse(report['ok'],index)
                self.assertNotIn(marker,json.dumps(report))

    def test_remote_package_excludes_php_and_server_environment(self):
        with tempfile.TemporaryDirectory() as t:
            for index,name in enumerate(['index.php','private/config.php','.env','.env.example']):
                p=create_ceapp.generate(Path(t)/str(index),'protected-demo','Protected','remote-web',url='https://example.com/app/',authorization='canengine')
                file=p/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text('SYNTHETIC_SERVER_ONLY_VALUE')
                report=validate_ceapp.validate(p)
                self.assertFalse(report['ok'],name)
                self.assertNotIn('SYNTHETIC_SERVER_ONLY_VALUE',json.dumps(report))

    def test_public_remote_template_uses_placeholder_url(self):
        m=json.loads((ROOT/'assets/remote-web/app.json').read_text())
        self.assertEqual(m['runtime']['remoteWeb']['url'],'https://example.com/app/')
        self.assertNotIn('authorization',m['runtime']['remoteWeb'])
        self.assertTrue(validate_ceapp.validate(ROOT/'assets/remote-web')['ok'])

    def test_unsafe_remote_declarations_fail(self):
        changes=[lambda m:m['runtime']['remoteWeb'].update(url='http://example.com'),lambda m:m['runtime']['remoteWeb'].update(url='https://secret@example.com'),lambda m:m['runtime']['remoteWeb'].update(allowedOrigins=['https://*.example.com']),lambda m:m['runtime']['remoteWeb'].update(allowedOrigins=['https://example.com/login']),lambda m:m.update(minCanEngineVersion='1.7.8'),lambda m:m.update(commands={'run':{'executable':'python3'}}),lambda m:m.update(capabilities={}),lambda m:m.update(permissions=['web.network','data.read'])]
        with tempfile.TemporaryDirectory() as t:
            for index,change in enumerate(changes):
                p=create_ceapp.generate(Path(t)/str(index),'remote','Remote','remote-web',url='https://example.com')
                m=json.loads((p/'app.json').read_text());change(m);(p/'app.json').write_text(json.dumps(m))
                self.assertFalse(validate_ceapp.validate(p)['ok'],m)

    def test_web_179_has_no_dummy_command(self):
        with tempfile.TemporaryDirectory() as t:
            p=create_ceapp.generate(Path(t)/'p','web','Web','web-python');m=json.loads((p/'app.json').read_text())
            self.assertEqual(m['minCanEngineVersion'],'1.8.0');self.assertEqual(m['commands'],{})
            m['runtime']['web']['network']='internet';(p/'app.json').write_text(json.dumps(m))
            self.assertFalse(validate_ceapp.validate(p)['ok'])

if __name__=='__main__':unittest.main(verbosity=2)
