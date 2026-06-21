# VISUAL REVIEW Role

Compare implementation against design ground truth.

## CLI (local)

```bash
graphcraft visual review .                    # all screens with reference_png
graphcraft visual review . --screen screen:login
graphcraft visual diff --reference .stitch/designs/login.png --candidate screenshots/login.png
```

Optional pixel diff: `pip install "MertCapkin_GraphCraft[visual]"` (Pillow).

Report: `graphcraft-out/VISUAL_REVIEW.md`

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

## Subagent invocation (Cursor Task)

When PNG candidates exist in `screenshots/`:

```
Task (generalPurpose or explore with vision):
  Read .cursor/skills/visual-review/VISUAL_REVIEW.md
  Run: graphcraft visual review .
  Compare graphcraft-out/VISUAL_REVIEW.md with implementation files from bridge.json
  Append findings to handoff/REVIEW.md under ## Visual Review
  Verdict: PASS | WARN | FAIL per screen
```

Do not skip CLI — agent adds qualitative notes on layout/spacing the pixel score cannot catch.
