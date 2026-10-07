import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

P = Path(__file__).resolve().parents[1] / 'scripts' / 'receive_delivery_fix2.py'
spec = importlib.util.spec_from_file_location('fix2_receive_test', P)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class TestFix2(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.base = Path(self.temp.name)
        self.root = self.base / 'repo'; self.root.mkdir(); self.old_pin = m.MANIFEST_SHA
        self.assets = []; self.files = {}; registry = {'assets': {}}
        for i in range(32):
            data = f'test-only-{i}'.encode()
            path = (m.PREFIXES[0] if i < 17 else m.PREFIXES[1]) + f'A{i}.png'
            a = dict(asset_id=f'A{i}', path=path, sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), kind='V5_ORIGINAL' if i < 17 else 'SOURCE')
            self.assets.append(a); self.files['P/payload/' + path] = data
            if i < 17:
                registry['assets'][f'A{i}'] = dict(a, status='CANDIDATE')
        self.raw = json.dumps(dict(delivery_id=m.DELIVERY_ID, assets=self.assets)).encode()
        m.MANIFEST_SHA = hashlib.sha256(self.raw).hexdigest()
        self.reg = self.root / 'assets/registry/generated_assets_v5.json'
        self.reg.parent.mkdir(parents=True); self.reg.write_text(json.dumps(registry))
        self.before = self.reg.read_bytes(); self.zip = self.base / 'bundle.zip'; self.make_zip()
    def make_zip(self, extra=None, raw=None):
        with zipfile.ZipFile(self.zip, 'w') as z:
            z.writestr('P/MEDIA_MANIFEST.json', self.raw if raw is None else raw)
            for k, v in self.files.items(): z.writestr(k, v)
            for k, v in extra or []: z.writestr(k, v)
    def tearDown(self):
        m.MANIFEST_SHA = self.old_pin; self.temp.cleanup()
    def test_dry_run_no_write(self):
        r=m.receive(self.root,self.zip);self.assertFalse(r['materials_received']);self.assertFalse((self.root/'local').exists())
    def test_import_and_check(self):
        r=m.receive(self.root,self.zip,True);self.assertEqual(r['imported_files'],32);self.assertEqual(m.check(self.root)['verified_files'],32)
    def test_repeat(self):
        m.receive(self.root,self.zip,True);r=m.receive(self.root,self.zip,True);self.assertEqual(r['imported_files'],0);self.assertEqual(r['already_present'],32)
    def test_no_approvals(self):
        r=m.receive(self.root,self.zip,True);self.assertEqual(self.reg.read_bytes(),self.before);self.assertFalse(r['production_ready']);self.assertFalse(r['full_remote_request_complete'])
    def test_corrupt_last_payload_no_write(self):
        self.files[list(self.files)[-1]]=b'bad';self.make_zip()
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
        self.assertFalse((self.root/'local').exists())
    def test_missing_payload_no_write(self):
        self.files.pop(list(self.files)[-1]);self.make_zip()
        with self.assertRaises(KeyError):m.receive(self.root,self.zip,True)
        self.assertFalse((self.root/'local').exists())
    def test_local_conflict_not_overwritten(self):
        p=self.root/self.assets[-1]['path'];p.parent.mkdir(parents=True);p.write_bytes(b'user-file')
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
        self.assertEqual(p.read_bytes(),b'user-file');self.assertFalse((self.root/self.assets[0]['path']).exists())
    def test_wrong_pin(self):
        self.make_zip(raw=self.raw+b' ')
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
    def test_traversal(self):
        self.make_zip(extra=[('P/../escape',b'no')])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
    def test_duplicate_zip_casefold(self):
        self.make_zip(extra=[('p/media_manifest.JSON',self.raw)])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
    def test_zip_symlink(self):
        zi=zipfile.ZipInfo('P/link');zi.create_system=3;zi.external_attr=(stat.S_IFLNK|0o777)<<16
        self.make_zip(extra=[(zi,b'/outside')])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
    def test_target_symlink(self):
        outside=self.base/'outside';outside.mkdir()
        try:(self.root/'local').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlink privilege not present')
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.zip,True)
        self.assertEqual(list(outside.iterdir()),[])
    def test_changed_import_detected(self):
        m.receive(self.root,self.zip,True);(self.root/self.assets[0]['path']).write_bytes(b'changed')
        with self.assertRaises(m.DeliveryError):m.check(self.root)
    def test_missing_registry(self):
        self.reg.unlink()
        with self.assertRaises(FileNotFoundError):m.receive(self.root,self.zip,True)
    def test_reserved_paths(self):
        for rel in ['C:/bad','../bad','local/NUL.png','local/x.','local/name:stream','local/x\\bad']:
            with self.assertRaises(m.DeliveryError):m.target(self.root,rel)
    def test_existing_lock_blocks(self):
        (self.root/'local').mkdir();(self.root/'local/.media-fix2.lock').write_text('another process')
        with self.assertRaises(FileExistsError):m.receive(self.root,self.zip,True)
        self.assertEqual((self.root/'local/.media-fix2.lock').read_text(),'another process')

if __name__ == '__main__':unittest.main()
