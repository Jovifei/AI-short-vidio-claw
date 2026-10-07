"""Metadata checks only. Real-media integration lives in the delivery VALIDATION.json."""
import json
from pathlib import Path, PurePosixPath
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ReceiptSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=json.loads((ROOT/'assets/registry/received_sources_20261007.json').read_text())
        cls.production=json.loads((ROOT/'assets/registry/generated_assets_v5.json').read_text())
    def test_counts(self):
        self.assertEqual(len(self.receipt['assets']),26)
        self.assertEqual(len({a['sha256'] for a in self.receipt['assets'].values()}),26)
    def test_original_v5_preserved(self):
        self.assertEqual(len(self.production['assets']),17)
        for aid,a in self.production['assets'].items():
            for key in ('path','sha256','bytes','width','height'):
                self.assertEqual(self.receipt['assets'][aid][key],a[key])
    def test_no_approval_granted(self):
        self.assertEqual(self.receipt['purpose'],'RECEIVE_ONLY_NOT_PRODUCTION_APPROVAL')
        for a in self.receipt['assets'].values():
            self.assertEqual(a['status'],'CANDIDATE');self.assertIsNone(a['approval_evidence'])
    def test_paths_and_hashes(self):
        for a in self.receipt['assets'].values():
            self.assertRegex(a['sha256'],r'^[0-9a-f]{64}$')
            p=PurePosixPath(a['path']);self.assertFalse(p.is_absolute());self.assertNotIn('..',p.parts)
            self.assertTrue(a['path'].startswith('local/references/'))
            self.assertGreater(a['bytes'],0);self.assertGreater(a['width'],0);self.assertGreater(a['height'],0)
if __name__=='__main__':unittest.main()
