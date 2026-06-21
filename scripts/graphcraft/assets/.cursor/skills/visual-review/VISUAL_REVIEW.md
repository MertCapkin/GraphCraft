# VISUAL REVIEW Role

Compare implementation against design ground truth.

## Checklist

- [ ] Stitch PNG match (if `.stitch/designs/` exists)
- [ ] Token usage matches design graph (no random hex)
- [ ] Touch targets ≥ config `design.touch_target_min`
- [ ] Safe area respected on mobile
- [ ] `graphcraft design harmony` PASS for reviewed screens

## Marketing + usability rubric

| Screen type | Marketing weight | Usability weight |
|-------------|------------------|------------------|
| shop, onboarding | high | medium |
| settings, forms | medium | high |

Report in `handoff/REVIEW.md` under `## Visual Review`.
