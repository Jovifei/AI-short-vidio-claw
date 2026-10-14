"""Synthetic runtime preflight; no actual requests, approval, or GPU execution."""
import json
from pathlib import Path
import unittest
import importlib
from datetime import datetime,timedelta
from zoneinfo import ZoneInfoNotFoundError
from unittest.mock import patch
from test_git_media_delivery import ROOT
import submit_prepared as submit
import fid1_deploy
import p1_comfy_probe


class Response:
    status=200
    def __init__(self,value):self.raw=json.dumps(value).encode()
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):return self.raw


class TemporalRuntimeTests(unittest.TestCase):
    def test_probe_import_without_timezone_database_has_current_utc8_timestamps(self):
        try:
            with patch('zoneinfo.ZoneInfo',side_effect=ZoneInfoNotFoundError('SYNTHETIC missing tzdata')):
                module=importlib.reload(p1_comfy_probe)
                self.assertEqual(datetime(2026,10,15,tzinfo=module.SHANGHAI).utcoffset(),timedelta(hours=8))
        finally:
            importlib.reload(p1_comfy_probe)

    def check(self,ram,gpu,name='FID1WanTemporalROIAnchor'):
        info={name:{'input':{'required':{'model':['MODEL'],'latent':['LATENT'],
            'roi_boxes_json':['STRING']}},'output':['MODEL','LATENT']}}
        if name=='FID1WanTemporalROIAnchor':info[name]['input']['required']['temporal_anchor_schedule_json']=['STRING']
        def get(request,**kwargs):
            return Response({'queue_running':[],'queue_pending':[]} if request.full_url.endswith('/queue') else info)
        job={'fid1_contract':{'node_class':name,'node_source_sha256':'0'*64}}
        with patch.object(fid1_deploy,'verify_installed',return_value={}), \
             patch.object(p1_comfy_probe,'sample_ram',return_value=ram), \
             patch.object(p1_comfy_probe,'sample_gpu',return_value=gpu), \
             patch.object(submit,'urlopen',side_effect=get):
            return submit.validate_fid1_runtime(ROOT,ROOT,job,'http://127.0.0.1:8188')

    def test_unknown_or_low_resources_fail_closed(self):
        good={'gpu_memory_total_mib':12282,'gpu_memory_used_mib':2000}
        for ram,gpu in [({},good),({'ram_avail_bytes':True},good),({'ram_avail_bytes':7*1024**3},good),
                        ({'ram_avail_bytes':9*1024**3},{}),
                        ({'ram_avail_bytes':9*1024**3},{'gpu_memory_total_mib':12282,'gpu_memory_used_mib':6000}),
                        ({'ram_avail_bytes':9*1024**3},{'gpu_memory_total_mib':12282,'gpu_memory_used_mib':-1}),
                        ({'ram_avail_bytes':9*1024**3},{'gpu_memory_total_mib':-1,'gpu_memory_used_mib':-10000}),
                        ({'ram_avail_bytes':9*1024**3},{'gpu_memory_total_mib':12282,'gpu_memory_used_mib':13000})]:
            with self.subTest(ram=ram,gpu=gpu),self.assertRaises(ValueError):self.check(ram,gpu)

    def test_resource_floor_is_reported_after_real_guard_path(self):
        result=self.check({'ram_avail_bytes':8*1024**3},{'gpu_memory_total_mib':12282,'gpu_memory_used_mib':2000})
        self.assertEqual(result['resources']['minimum_ram_available_bytes'],8*1024**3)
        self.assertTrue(result['resources']['snapshot_not_peak_guarantee'])

    def test_v4_uses_same_resource_guard_without_temporal_socket(self):
        # Resource helper sends temporal socket only for v3, exact original sockets for v4.
        good={'gpu_memory_total_mib':12282,'gpu_memory_used_mib':2000}
        for ram,gpu in [({},good),({'ram_avail_bytes':7*1024**3},good),({'ram_avail_bytes':8*1024**3},{}),({'ram_avail_bytes':8*1024**3},{'gpu_memory_total_mib':12282,'gpu_memory_used_mib':-1})]:
            with self.subTest(ram=ram,gpu=gpu),self.assertRaises(ValueError):
                self.check(ram,gpu,'FID1WanStrengthROIAnchor')
        result=self.check({'ram_avail_bytes':8*1024**3},good,'FID1WanStrengthROIAnchor')
        self.assertEqual(result['loaded_node_class'],'FID1WanStrengthROIAnchor')
