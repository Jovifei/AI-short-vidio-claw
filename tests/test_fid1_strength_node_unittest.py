"""Real full-size CPU Tensor contracts; no GPU or visual acceptance."""
import copy
import json
import unittest
import torch
from pathlib import Path
import test_fid1_timestep_aware_node_unittest as fixtures
from scripts import fid1_wan_latent_anchor_node as node

ROIS=json.loads((Path(__file__).resolve().parents[1]/'config/source_fidelity_trials/SH903_FID1_V008.json').read_text())['anchor_rois']


class StrengthNodeTests(unittest.TestCase):
    def latent(self):
        samples=torch.full((1,48,13,64,36),99.);samples[:,:,0]=7.
        mask=torch.ones((1,1,13,64,36));mask[:,:,0]=0
        return {'samples':samples,'noise_mask':mask,'metadata':{'fixture':True}}

    def test_full_size_strength_alpha_once_trajectory_and_metadata(self):
        latent=self.latent();patcher=fixtures.FakeModelPatcher(fixtures.WAN22())
        model,out=node.FID1WanStrengthROIAnchor().anchor(patcher,latent,json.dumps(ROIS))
        self.assertIs(out['noise_mask'],latent['noise_mask']);self.assertIs(out['metadata'],latent['metadata'])
        self.assertEqual(patcher.model_options,{})
        self.assertTrue(torch.equal(out['samples'][:,:,1:,0,0],latent['samples'][:,:,1:,0,0]))
        self.assertTrue(torch.equal(out['samples'][:,:,0],latent['samples'][:,:,0]))
        mask=model.model_options['denoise_mask_function'](.5,latent['noise_mask'])
        for y,x,strength in ((16,7,.55),(16,28,.55),(15,18,.65)):
            self.assertTrue(torch.allclose(mask[:,:,1:,y,x],torch.full_like(mask[:,:,1:,y,x],1-strength)))
            self.assertTrue(torch.equal(out['samples'][:,:,1:,y,x],torch.full_like(out['samples'][:,:,1:,y,x],7)))
            blend=out['samples']*(1-mask)
            self.assertAlmostEqual(float(blend[0,0,1,y,x]),7*strength,places=5)
        self.assertTrue(torch.equal(mask[:,:,1:,0,0],torch.ones_like(mask[:,:,1:,0,0])))
        # feather distance1 at y13,x7 => .25*.55, not strength squared.
        self.assertAlmostEqual(float(mask[0,0,1,13,7]),1-.25*.55,places=6)
        noise=torch.ones_like(out['samples']);scaled=model.object_patches['scale_latent_inpaint'](.25,noise,out['samples'])
        expected=model.get_model_object('model_sampling').noise_scaling(.25,noise,out['samples'])
        self.assertTrue(torch.equal(scaled[:,:,1:,16,7],expected[:,:,1:,16,7]))
        self.assertTrue(torch.equal(scaled[:,:,0],out['samples'][:,:,0]))
        repeated=latent['noise_mask'].repeat(1,48,1,1,1)
        self.assertTrue(torch.equal(model.model_options['denoise_mask_function'](.5,repeated),mask.expand_as(repeated)))
        with self.assertRaisesRegex(ValueError,'dtype/device'):
            model.model_options['denoise_mask_function'](.5,latent['noise_mask'].double())
        with self.assertRaisesRegex(ValueError,'dtype/device'):
            model.model_options['denoise_mask_function'](.5,latent['noise_mask'].to('meta'))

    def test_strength_negative_admission_and_overlap(self):
        for value in (True,'0.55',0,1,.2,.81,float('nan'),float('inf')):
            bad=copy.deepcopy(ROIS);bad[0]['preserve_strength']=value
            with self.subTest(value=value),self.assertRaises(ValueError):node._anchor_future_rois_strength(self.latent(),bad)
        for change in ('duplicate','overlap','extra','missing','feather'):
            bad=copy.deepcopy(ROIS)
            if change=='duplicate':bad[1]['id']=bad[0]['id']
            if change=='overlap':bad[2].update(x0=.12,x1=.30,y0=.21,y1=.32)
            if change=='extra':bad[0]['temporal_anchor_schedule']=[1]*12
            if change=='missing':del bad[0]['preserve_strength']
            if change=='feather':bad[0]['feather_latent']=0
            with self.subTest(change=change),self.assertRaises(ValueError):node._anchor_future_rois_strength(self.latent(),bad)

    def test_legacy_v2_v3_numeric_equivalence_remains(self):
        latent=fixtures.sample_latent();model=fixtures.FakeModelPatcher(fixtures.WAN22())
        v2,a=node.anchor_future_rois_timestep_aware(model,latent,fixtures.ROIS)
        v3,b=node.anchor_future_rois_temporal(model,latent,fixtures.ROIS,[1]*12)
        self.assertTrue(torch.equal(a['samples'],b['samples']))
        self.assertTrue(torch.equal(v2.model_options['denoise_mask_function'](.5,latent['noise_mask']),v3.model_options['denoise_mask_function'](.5,latent['noise_mask'])))
        self.assertEqual(set(node.FID1WanStrengthROIAnchor.INPUT_TYPES()['required']),{'model','latent','roi_boxes_json'})

    def test_v4_full_shape_tensor_and_sampler_mask_failures(self):
        for change in ('channels','time','nan','mask_dtype','base_mask'):
            latent=self.latent()
            if change=='channels':latent['samples']=latent['samples'][:,:47]
            if change=='time':latent['samples']=latent['samples'][:,:,:12]
            if change=='nan':latent['samples'][0,0,1,0,0]=float('nan')
            if change=='mask_dtype':latent['noise_mask']=latent['noise_mask'].double()
            if change=='base_mask':latent['noise_mask'][0,0,0,0,0]=1
            with self.subTest(change=change),self.assertRaises(ValueError):
                node.FID1WanStrengthROIAnchor().anchor(fixtures.FakeModelPatcher(fixtures.WAN22()),latent,json.dumps(ROIS))
        latent=self.latent();model,_=node.FID1WanStrengthROIAnchor().anchor(fixtures.FakeModelPatcher(fixtures.WAN22()),latent,json.dumps(ROIS))
        hook=model.model_options['denoise_mask_function']
        for change in ('nonrepeat','nonfinite','base','shape'):
            mask=latent['noise_mask'].repeat(1,48,1,1,1)
            if change=='nonrepeat':mask[0,1,1,0,0]=0
            if change=='nonfinite':mask[:,:,:,0,0]=float('inf')
            if change=='base':mask[:,:,0]=1
            if change=='shape':mask=mask[:,:,:12]
            with self.subTest(change=change),self.assertRaises(ValueError):hook(.5,mask)
        for change in ('coordinate','area','missing'):
            bad=copy.deepcopy(ROIS)
            if change=='coordinate':bad[0]['x0']=-.1
            if change=='area':bad[0].update(x0=0,y0=0,x1=1,y1=1)
            if change=='missing':del bad[0]['x0']
            with self.subTest(change=change),self.assertRaises(ValueError):node._anchor_future_rois_strength(latent,bad)
