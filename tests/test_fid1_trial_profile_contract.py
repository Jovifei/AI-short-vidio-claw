import json
from pathlib import Path

PROFILE = Path('config/source_fidelity_trials/SH903_FID1_V001.json')


def test_fid1_profile_is_source_trial_only():
    data = json.loads(PROFILE.read_text(encoding='utf-8'))
    assert data['scope'] == 'T1_SOURCE_ONLY'
    assert data['shot_id'] == 'SH903'
    assert data['frames'] == 49
    assert data['fps'] == 24


def test_fid1_does_not_expand_production_scope():
    data = json.loads(PROFILE.read_text(encoding='utf-8'))
    assert 'EP001' not in data['shot_id']
    assert 'LOOKREEL' not in data['scope']


def test_fid1_keeps_wan5b_boundary_in_metadata_contract():
    text = PROFILE.read_text(encoding='utf-8')
    assert '14B' not in text
    assert 'LoRA' not in text
    assert 'platform' not in text.lower()
