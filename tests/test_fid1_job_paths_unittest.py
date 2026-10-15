"""Canonical paths are checked before writes; all data is synthetic temporary data."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from test_git_media_delivery import ROOT
import fid1_job_paths as paths


class JobPathTests(unittest.TestCase):
    def test_three_shots_accept_only_their_own_standard_take(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for shot in ('SH901','SH902','SH903'):
                rel=f'{paths.LOCAL}/video/{shot}/jobs/take02'
                self.assertEqual(paths.canonical_job_directory(root,rel,shot),root/rel)
                self.assertFalse((root/rel).exists())
                for wrong in (rel.replace(shot,'SH999'), rel.replace('take02','quality_take02'),
                              rel.replace('take02','take2'), rel+'/..', rel+'/child',
                              rel.replace('T1_SOURCE_PILOT','EP001')):
                    with self.subTest(wrong=wrong),self.assertRaises(ValueError):
                        paths.canonical_job_directory(root,wrong,shot)

    def test_raw_dot_and_escape_not_normalized_away(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for value in ('local/../local/a','local/./a','../outside',str(root.parent/'outside'),
                          str(root)+'/local/../local/a'):
                with self.subTest(value=value),self.assertRaises(ValueError):
                    paths.safe_project_path(root,value)

    def test_reparse_and_same_root_alias_refused_without_privilege_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);rel=f'{paths.LOCAL}/video/SH903/jobs/take02'
            flagged=root/'local';original=Path.is_symlink
            with patch.object(Path,'is_symlink',lambda p:p==flagged or original(p)),self.assertRaises(ValueError):
                paths.canonical_job_directory(root,rel,'SH903')
            original_stat=Path.lstat
            def attrs(p,*args,**kwargs):
                if p==flagged:return SimpleNamespace(st_file_attributes=0x400,st_mode=0)
                return original_stat(p,*args,**kwargs)
            with patch.object(Path,'lstat',attrs),self.assertRaises(ValueError):
                paths.canonical_job_directory(root,rel,'SH903')
