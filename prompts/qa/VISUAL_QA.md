# Visual QA Prompt / Checklist

Evaluate the current image or clip against the approved references.

## Identity
- Is DAIYU clearly the same approved face?
- Is WUKONG clearly the same approved simian face?
- Has either character become a generic modern face?

## Costume
- Are approved classical costumes preserved?
- Is there any modern character clothing?

## Anatomy
- Correct number of limbs/fingers?
- Contact points plausible?
- Mirror/reflection consistent?

## Continuity
- Correct stage?
- Bandage/umbrella/weather state correct?
- Props persist correctly?

## Chemistry
- Does the interaction read as familiar and natural?
- Is the pose too staged or poster-like?

## Motion
For video:
- identity preserved through time?
- background stable?
- action completes?
- end frame usable?

## Output
Return:
- PASS / FAIL
- hard failure reason code
- scores 1–5 for identity, costume, anatomy, continuity, chemistry, motion
- recommended next action: accept / local edit / reroll / static fallback
