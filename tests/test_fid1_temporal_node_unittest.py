"""Real Torch CPU arithmetic; synthetic models are not GPU acceptance."""
import json
import unittest
import torch
import test_fid1_timestep_aware_node_unittest as fixtures
from scripts import fid1_wan_latent_anchor_node as node

SCHEDULE = [1,1,1,1,.9,.8,.7,.6,.6,.6,.6,.6]


class TemporalNodeTests(unittest.TestCase):
    def test_all_one_schedule_exactly_matches_v2(self):
        latent=fixtures.sample_latent();model=fixtures.FakeModelPatcher(fixtures.WAN22())
        old,old_latent=node.anchor_future_rois_timestep_aware(model,latent,fixtures.ROIS)
        new,new_latent=node.anchor_future_rois_temporal(model,latent,fixtures.ROIS,[1]*12)
        self.assertTrue(torch.equal(old_latent['samples'],new_latent['samples']))
        self.assertIs(new_latent['noise_mask'],latent['noise_mask'])
        for sigma in (.1,.5,1):
            self.assertTrue(torch.equal(old.model_options['denoise_mask_function'](sigma,latent['noise_mask']),
                                        new.model_options['denoise_mask_function'](sigma,latent['noise_mask'])))
            noise=torch.ones_like(latent['samples'])
            self.assertTrue(torch.equal(old.object_patches['scale_latent_inpaint'](sigma,noise,old_latent['samples']),
                                        new.object_patches['scale_latent_inpaint'](sigma,noise,new_latent['samples'])))

    def test_schedule_scales_spatial_alpha_once_and_keeps_noise_trajectory(self):
        samples=torch.full((1,48,13,20,20),99.);samples[:,:,0]=7.
        mask=torch.ones((1,1,13,20,20));mask[:,:,0]=0
        latent={'samples':samples,'noise_mask':mask,'metadata':'preserved'}
        rois=[dict(id='FACE',x0=1/20,y0=1/20,x1=13/20,y1=13/20,feather_latent=4)]
        model,out=node.anchor_future_rois_temporal(fixtures.FakeModelPatcher(fixtures.WAN22()),latent,rois,SCHEDULE)
        sampler_mask=model.model_options['denoise_mask_function'](.5,mask)
        self.assertIs(out['noise_mask'],mask);self.assertEqual(out['metadata'],'preserved')
        self.assertTrue(torch.equal(out['samples'][:,:,0],samples[:,:,0]))
        self.assertTrue(torch.equal(out['samples'][:,:,:,0,0],samples[:,:,:,0,0]))
        for t,weight in enumerate(SCHEDULE,1):
            # spatial alpha=.25 at y2,x6; source is copied completely, alpha used by sampler once.
            self.assertEqual(float(out['samples'][0,0,t,2,6]),7.)
            self.assertAlmostEqual(float(sampler_mask[0,0,t,2,6]),1-.25*weight)
            blended=out['samples']*(1-sampler_mask)
            self.assertAlmostEqual(float(blended[0,0,t,2,6]),7*.25*weight,places=5)
        self.assertTrue(torch.equal(sampler_mask[:,:,:,0,0],mask[:,:,:,0,0]))
        noise=torch.full_like(samples,2.)
        scaled=model.object_patches['scale_latent_inpaint'](.25,noise,out['samples'])
        expected=model.get_model_object('model_sampling').noise_scaling(.25,noise,out['samples'])
        self.assertTrue(torch.equal(scaled[:,:,1:,2,6],expected[:,:,1:,2,6]))
        self.assertTrue(torch.equal(scaled[:,:,0],out['samples'][:,:,0]))
        repeated=mask.repeat(1,48,1,1,1)
        self.assertTrue(torch.equal(model.model_options['denoise_mask_function'](.5,repeated),sampler_mask.expand_as(repeated)))

    def test_bad_schedules_rejected(self):
        for schedule in (None,[1]*11,[1]*13,[True]*12,[float('nan')]*12,[float('inf')]*12,
                         [.9]*12,[1]*4+[.5]*8,[1]*4+[1.1]*8,[1,.6,.7]+[.6]*9):
            with self.subTest(schedule=schedule),self.assertRaises(ValueError):
                node.anchor_future_rois_temporal(fixtures.FakeModelPatcher(fixtures.WAN22()),fixtures.sample_latent(),fixtures.ROIS,schedule)

    def test_node_ports_and_schedule_json_errors(self):
        cls=node.FID1WanTemporalROIAnchor
        self.assertEqual(cls.RETURN_TYPES,('MODEL','LATENT'))
        self.assertEqual(set(cls.INPUT_TYPES()['required']),{'model','latent','roi_boxes_json','temporal_anchor_schedule_json'})
        with self.assertRaises(ValueError):
            cls().anchor(fixtures.FakeModelPatcher(fixtures.WAN22()),fixtures.sample_latent(),json.dumps(fixtures.ROIS),'not-json')

    def test_v3_rejects_tensor_and_roi_admission_failures(self):
        for change in ('channels','time','nonfinite','dtype','base_mask'):
            latent=fixtures.sample_latent()
            if change=='channels':latent['samples']=latent['samples'][:,:47]
            if change=='time':latent['samples']=latent['samples'][:,:,:12]
            if change=='nonfinite':latent['samples'][0,0,1,0,0]=float('nan')
            if change=='dtype':latent['noise_mask']=latent['noise_mask'].double()
            if change=='base_mask':latent['noise_mask'][0,0,1,0,0]=0
            with self.subTest(change=change),self.assertRaises(ValueError):
                node.anchor_future_rois_temporal(fixtures.FakeModelPatcher(fixtures.WAN22()),latent,fixtures.ROIS,SCHEDULE)
        for rois in ([dict(id='LARGE',x0=0,y0=0,x1=1,y1=1)],fixtures.ROIS*9):
            with self.assertRaises(ValueError):
                node.anchor_future_rois_temporal(fixtures.FakeModelPatcher(fixtures.WAN22()),fixtures.sample_latent(),rois,SCHEDULE)
