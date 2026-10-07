import importlib.util
import json
import hashlib
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'scripts' / 'receive_media_v5.py'
spec = importlib.util.spec_from_file_location('receive_media_v5', P)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class TestMediaReceive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.base = Path(self.tmp.name)
        self.root = self.base/'repo'; self.root.mkdir(); self.old_hash = m.MANIFEST_SHA256
        self.assets = []; self.payload = {}; self.reg = {'schema_version':5,'assets':{}}
        for i in range(32):
            data = ('valid-png-test-fixture-'+str(i)).encode()
            aid = 'A'+str(i); rel=f'local/references/generated/20261005_v5/{aid}.png' if i < 17 else f'local/references/recovery_20261007/{aid}.png'
            a={'asset_id':aid,'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'kind':'V5_ORIGINAL' if i<17 else 'SOURCE_OPTION'}
            self.assets.append(a); self.payload['pack/payload/'+rel]=data
            if i<17:self.reg['assets'][aid]=dict(a,status='CANDIDATE')
        self.d={'delivery_id':m.DELIVERY_ID,'assets':self.assets}; self.raw=json.dumps(self.d).encode()
        m.MANIFEST_SHA256=hashlib.sha256(self.raw).hexdigest()
        r=self.root/'assets/registry/generated_assets_v5.json';r.parent.mkdir(parents=True);r.write_text(json.dumps(self.reg))
        self.reg_before=r.read_bytes(); self.z=self.base/'bundle.zip';self.make_zip()
    def tearDown(self):
        m.MANIFEST_SHA256=self.old_hash;self.tmp.cleanup()
    def make_zip(self, payload=None, raw=None, extra=None):
        with zipfile.ZipFile(self.z,'w') as z:
            z.writestr('pack/MEDIA_MANIFEST.json',self.raw if raw is None else raw)
            for k,v in (self.payload if payload is None else payload).items():z.writestr(k,v)
            for k,v in (extra or []):z.writestr(k,v)
    def test_dry_run_has_no_local_write(self):
        r=m.receive(self.root,self.z);self.assertEqual(r['planned_imports'],32);self.assertFalse((self.root/'local').exists());self.assertFalse(r['materials_received'])
    def test_import_and_check(self):
        r=m.receive(self.root,self.z,True);self.assertEqual(r['imported_files'],32);self.assertFalse(r['production_ready']);self.assertEqual(m.check(self.root)['verified_files'],32)
    def test_idempotent(self):
        m.receive(self.root,self.z,True);r=m.receive(self.root,self.z,True);self.assertEqual(r['already_present'],32);self.assertEqual(r['imported_files'],0)
    def test_registry_and_approvals_untouched(self):
        m.receive(self.root,self.z,True);self.assertEqual((self.root/'assets/registry/generated_assets_v5.json').read_bytes(),self.reg_before)
    def test_late_corruption_no_write(self):
        pp=dict(self.payload);pp[list(pp)[-1]]=b'bad';self.make_zip(payload=pp)
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
        self.assertFalse((self.root/'local').exists())
    def test_missing_asset_no_write(self):
        pp=dict(self.payload);pp.pop(list(pp)[-1]);self.make_zip(payload=pp)
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
        self.assertFalse((self.root/'local').exists())
    def test_existing_conflict_preserved(self):
        p=self.root/self.assets[-1]['path'];p.parent.mkdir(parents=True);p.write_bytes(b'USER FILE')
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
        self.assertEqual(p.read_bytes(),b'USER FILE');self.assertFalse((self.root/self.assets[0]['path']).exists())
    def test_wrong_manifest_hash(self):
        self.make_zip(raw=self.raw+b' ')
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_traversal_member_rejected(self):
        self.make_zip(extra=[('pack/../../escape',b'bad')])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_archive_symlink_rejected(self):
        zi=zipfile.ZipInfo('pack/link');zi.create_system=3;zi.external_attr=(stat.S_IFLNK|0o777)<<16
        self.make_zip(extra=[(zi,b'/outside')])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_duplicate_archive_name_rejected(self):
        self.make_zip(extra=[('PACK/MEDIA_MANIFEST.JSON',self.raw)])
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_target_symlink_rejected(self):
        external=self.base/'external';external.mkdir();(self.root/'local').symlink_to(external,target_is_directory=True)
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
        self.assertFalse(list(external.iterdir()))
    def test_missing_repository_registry(self):
        (self.root/'assets/registry/generated_assets_v5.json').unlink()
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_wrong_registry_hash(self):
        self.reg['assets']['A16']['sha256']='0'*64;(self.root/'assets/registry/generated_assets_v5.json').write_text(json.dumps(self.reg))
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)
    def test_check_detects_changed_file(self):
        m.receive(self.root,self.z,True);(self.root/self.assets[0]['path']).write_bytes(b'changed')
        with self.assertRaises(m.DeliveryError):m.check(self.root)
    def test_check_before_import_blocked(self):
        with self.assertRaises(m.DeliveryError):m.check(self.root)
    def test_unsafe_windows_path(self):
        for path in ('C:/evil.png','/tmp/evil.png','../evil.png','local/name:stream','local/.. /x','local/x.'):
            with self.assertRaises(m.DeliveryError):m.under(self.root,path)
    def test_empty_zip_is_not_a_delivery(self):
        with zipfile.ZipFile(self.z,'w'):pass
        with self.assertRaises(m.DeliveryError):m.receive(self.root,self.z,True)

if __name__=='__main__':unittest.main()
