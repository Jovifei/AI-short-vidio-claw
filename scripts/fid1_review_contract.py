"""Strict human feedback fields shared by recording and predecessor admission."""
from datetime import datetime
import re

try:
    from .preproduction import require
except ImportError:
    from preproduction import require


REVIEW_FIELDS = {
    'schema_version', 'scope', 'shot_id', 'profile_id', 'output_sha256', 'decision',
    'full_playback', 'identity', 'costume', 'limbs', 'reviewer', 'user_quote', 'recorded_at',
}
VISUAL_CRITERIA = ('full_playback', 'identity', 'costume', 'limbs')


def validate_visual_review_payload(review, *, scope, shot_id, profile_id, output_sha256):
    require(isinstance(review, dict) and set(review) == REVIEW_FIELDS
            and type(review.get('schema_version')) is int and review['schema_version'] == 1,
            'visual review fields/schema are invalid')
    require(review.get('scope') == scope and review.get('shot_id') == shot_id
            and review.get('profile_id') == profile_id, 'visual review belongs to another source trial')
    require(isinstance(output_sha256, str) and re.fullmatch(r'[0-9a-f]{64}', output_sha256)
            and review.get('output_sha256') == output_sha256,
            'visual review is not bound to this output hash')
    require(review.get('reviewer') == 'Jovi' and isinstance(review.get('user_quote'), str)
            and 0 < len(review['user_quote'].strip()) and len(review['user_quote']) <= 2048,
            "review requires Jovi's explicit words")
    try:
        recorded = datetime.fromisoformat(review['recorded_at'].replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('visual review timestamp must be ISO-8601 with timezone') from exc
    require(recorded.tzinfo is not None and recorded.utcoffset() is not None,
            'visual review timestamp must include timezone')
    require(all(isinstance(review.get(key), str)
                and review[key] in {'PASS', 'CHANGES_REQUIRED', 'NOT_RUN'} for key in VISUAL_CRITERIA),
            'visual review statuses must be PASS, CHANGES_REQUIRED, or NOT_RUN')
    decision = review.get('decision')
    require(isinstance(decision, str) and decision in {'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL', 'CHANGES_REQUIRED'},
            'invalid visual review decision')
    if decision == 'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL':
        require(all(review[key] == 'PASS' for key in VISUAL_CRITERIA),
                'next source-only trial requires PASS for full playback, identity, costume, and limbs')
    else:
        require(any(review[key] != 'PASS' for key in VISUAL_CRITERIA),
                'CHANGES_REQUIRED needs at least one unresolved or failed visual criterion')
    return True
