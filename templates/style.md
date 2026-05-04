<!--
Template lifted from PUSHING FRAMES (github.com/PUSHINGSQUARES/pushing-frames).
Format must remain compatible — projects authored here open cleanly in PUSHING FRAMES.
-->
---
title: Cinematography Rules — Starter Library
author: pushing-frames-defaults
pack_version: '0.1'
template_id: cinematography
---

<!--
THE THESIS

Stop prompting. Start defining outcomes.

The single biggest unlock in image generation isn't a model upgrade or a
seed trick—it's treating the AI like a DP you've hired for the day.
You don't tell a director of photography "make it cinematic". You tell
them ARRI Alexa 35, 50mm prime at T1.5, golden-hour rim from frame
right, anamorphic squeeze, 24fps at 1/48 shutter, and you hand them
three reference images.

Specificity isn't decoration. It's how you transfer 12 years of being
on set into a sentence the model can act on.

Three principles every block in this library is built around:

  1. Provide the brief a real DP would need. Camera, rig, lens, T-stop,
     shutter, fps, lighting state and direction, focal subject, time of
     day. Vague is a creative coward's hedge—the model fills the vagueness
     with the most generic option in its training data.

  2. References do the heavy lifting. Words narrow. Images aim. Drop
     references for skin tone, fabric texture, vehicle livery, location
     mood—anything you can show instead of describe.

  3. Negative blocks fight defaults. The plastic-skin centred-front-lit
     hero shot is the AI's default not because it's good, but because
     it's the average of the training data. Pull against the average
     loudly and consistently.

This template is a curated library of STYLE_ and NEG_ blocks named by
intent so you can mix-and-match per shot. Toggle what fits the project,
drop the rest, replace bodies with your own language as you build a
personal voice.
-->

<!--
WHY: a baseline that anchors every shot to "this was photographed with a real
camera by a real cinematographer", not "this was rendered by a model that
trained on Pinterest". Lead every prompt with a "Shot on …" call and this
block lets you avoid repeating the rationale.
-->
## STYLE_PHOTOREAL_BASE
photorealistic textures, real-world physics, natural skin pores, fabric weave visible, micro-imperfections, scratches, dust, fingerprints—shot on professional cinema equipment by a working DP, not rendered. high dynamic range, natural depth of field falloff. no AI-clean.

<!--
WHY: Kodak Vision3 stocks are a reliable shorthand for the "expensive feature
film" look. 50D is daylight-balanced fine grain (commercials, hero exteriors).
2383 is the print stock—slight crush in shadows, controlled highlights, the
"projected in a cinema" feel. Mentioning both stops models from picking the
wrong neutral digital look.
-->
## STYLE_KODAK_VISION
kodak vision3 50d daylight stock with kodak 2383 print emulation, gentle highlight rolloff, subtle shadow crush, warm neutral midtones, organic colour science—not log, not raw, finished print look.

<!--
WHY: anamorphic glass leaves visible fingerprints—horizontal blue streak
flares, oval out-of-focus highlights, edge breathing, complex chromatic
aberration in dust and spray. Stating the squeeze ratio (2x) gives the
model the strongest cue. Use this block when you want "feature film",
not "ad-shoot clean".
-->
## STYLE_ANAMORPHIC
anamorphic 2x squeeze, horizontal blue streak lens flares, elliptical bokeh, edge breathing toward frame corners, complex chromatic aberration in highlights and dust motes, subtle barrel breathing on focus pulls.

<!--
WHY: most AI defaults to noon-flat. Calling out time of day and direction
of light is the single biggest legibility win. Golden hour reads as warm
key + cool fill, hard rim along one edge of the subject—the opposite of
the symmetrical bounce a model defaults to.
-->
## STYLE_GOLDEN_HOUR
late afternoon golden hour, low angled key from frame right casting long shadows, warm rim along subject edge, cooler fill from open sky, no overhead noon sun, no symmetrical lighting—directional and falling off.

<!--
WHY: the alternative weather call. Overcast diffused removes harsh
shadows but should still feel directional from sky brightness. Useful
for editorial portraits, automotive on wet tarmac, anything that needs
texture without theatrical contrast.
-->
## STYLE_OVERCAST_DIFFUSED
overcast british sky, soft directional light from above-left, low contrast but still shaped, wet pavement holding reflections, no hard shadows, no studio softbox uniformity.

<!--
WHY: low-light state. AI defaults are often "flat dim with no source"—
calling out sodium streetlamp, neon practicals, or a single hard window
gives the model a light source to motivate from. Halation reads strongest
in low-light highlights; lean on it here.
-->
## STYLE_LOW_LIGHT_PRACTICALS
night-time, motivated by named practical sources—neon signage, tungsten window spill, sodium streetlamp—each casting its own colour. heavy halation around bright bulbs, deep shadows held with detail not crushed, no flat dim ambient.

<!--
WHY: shallow DOF is what most users mean by "cinematic". Specify the
T-stop and lens length—T1.5 on a 50mm reads completely differently from
T2.8 on a 24mm. Without explicit DOF call, models tend to default to
deep-focus everything-sharp, which kills the read.
-->
## STYLE_SHALLOW_DOF
extremely shallow depth of field at T1.5—T2.0 on cine prime, focus locked tight on subject's eyes/hands, foreground and background falling off into creamy out-of-focus, organic falloff not gaussian-blur fake.

<!--
WHY: macro/tactile feel. Reach for this on close-ups of hands, materials,
mechanical detail. The model otherwise defaults to mid-shot framing even
when prompted "extreme close-up". Naming dust motes and texture forces
the macro read.
-->
## STYLE_MACRO_TACTILE
extreme macro close-up, dust motes catching directional light, fingerprint smears on glass, fabric weave at thread level, micro chromatic aberration on metal edges, breath fog on cold surfaces.

<!--
WHY: film grain is best as a felt presence, not a heavy effect. "Subtle"
is the operative word. Models tend to either give you zero grain
(plastic) or a heavy noise overlay (broken). Specifying the stock and
"subtle" stops both failures.
-->
## STYLE_GRAIN_HALATION
subtle 35mm film grain visible in shadows and skin midtones, halation bleeding around clipped highlights, micro chromatic aberration on hard edges, soft bloom on bright sources—analogue interference, not noise.

<!--
WHY: handheld camera character. The model often reads "handheld" as
"shaky cam"—calling out organic breathing, slight rack focus, parallax
from operator weight gives the right kind of movement.
-->
## STYLE_HANDHELD_OPERATOR
handheld with experienced operator, organic micro-breathing, subtle weight shifts on each step, slight rack focus between subjects, parallax that feels human—not gimbal-smooth, not shaky-cam.

<!--
WHY: composition rule. AI loves centred symmetrical hero shots because
its training data is full of them. Calling out off-centre, leading lines,
or rule-of-thirds anchors actively pushes against that default.
-->
## STYLE_COMPOSITION_OFFCENTRE
subject placed on rule-of-thirds intersection or in negative-space asymmetry, leading lines drawing eye through frame, shoulders or steering wheel breaking edge, never centred-front-on hero portrait.

<!--
WHY: skin and faces. The single biggest AI tell is plastic-smooth skin
with too-symmetrical features. Calling out pores, asymmetry, and "human"
imperfections is more effective than relying on negative prompts alone.
-->
## STYLE_REAL_SKIN
visible skin pores, individual hair strands at hairline, slight facial asymmetry, subtle ruddiness in cheeks and ears, fine lines around eyes if appropriate to age, micro-imperfections—nobody is airbrushed.

<!--
WHY: anti-AI face/skin failure modes. Most models smooth skin like an
Instagram filter on default; this block fights that hard.
-->
## NEG_AI_PLASTIC_SKIN
plastic skin, smooth airbrushed skin, doll-like, mannequin, waxy, porcelain, instagram filter, beauty filter, smoothed pores, symmetrical face, perfect teeth, perfect makeup, photoshop liquify, plumped lips, identical eyes.

<!--
WHY: anti-AI composition failure modes. The default centred front-lit
hero with symmetrical lighting is the most common AI tell after the
plastic skin. Worth its own block.
-->
## NEG_AI_COMPOSITION
centred front-lit hero shot, symmetrical lighting, balanced studio softbox setup, corporate headshot framing, dead-centre subject, magazine-cover staging, every-feature-evenly-lit, no shadow side, generic stock photo.

<!--
WHY: anti-AI lighting failures. Flat noon, ambient-only, glow-without-source,
"everything golden" without direction. AI lighting fails by being too even
or too "look I added a flare".
-->
## NEG_AI_LIGHTING
flat noon lighting, evenly-lit ambient, glow without source direction, fake lens flare overlay, every-light-balanced, studio softbox uniformity, ringlight beauty look, ambient-occlusion-fake, "golden filter" applied evenly.

<!--
WHY: human anatomy failures. Standard model failure modes the major
image gen models still trip on. Worth keeping as a separate block from
NEG_AI_PLASTIC_SKIN so you can mix.
-->
## NEG_HUMAN_ANATOMY
deformed hands, extra fingers, missing fingers, fused fingers, distorted fingers, bad anatomy, bad proportions, extra limbs, missing limbs, floating limbs, disconnected limbs, mutated faces, mutation, disfigured, bad eyes, crossed eyes, bad teeth, asymmetric features in error, clothing glitches, merging clothes, impossible pose.

<!--
WHY: object/vehicle failures. Generic enough to apply to most "thing in
frame" subjects—cars, motorcycles, hardware, machinery. Customise per
project (rename to NEG_CAR_GLITCH, NEG_PRODUCT_GLITCH, etc.) when you
want to be specific.
-->
## NEG_OBJECT_GEOMETRY
deformed geometry, distorted proportions, extra parts, missing parts, bad perspective, melted edges, ugly, blurry, low quality, watermark, text, writing, signature, logo glitches, broken physics, impossible reflection.

<!--
WHY: anti-influencer aesthetic. Most AI-trained images are skewed toward
travel-influencer "everything golden, everything dreamy" looks. This
block pulls explicitly away from that mood.
-->
## NEG_INFLUENCER_AESTHETIC
travel-influencer aesthetic, everything-dreamy, all-golden-filter, soft-glowy-everywhere, "main character" framing, instagram preset look, lifestyle stock photo, polished commercial sheen.

# Notes

The whole game is treating the model like a DP you've hired. Hand it the brief a real director of photography would need on the day. Vague prompts produce average results because models default to the average of their training data—specificity is how you escape that average.

Lead with "Shot on [camera]" or "Shot on [camera] mounted on [rig]" at the start of every shot's action description. State T-stop and shutter speed. Naming the specific prime length (24mm, 50mm, 85mm) biases the field of view and depth of field more reliably than a generic description.

For rigs, be specific—Steadicam, U-Crane (Russian Arm), Black Arm tracking buggy, helicopter gimbal, FPV drone. The model reads rig terminology as movement cues better than plain "tracking shot".

Specify only the blocks the shot needs. A close-up macro probably wants STYLE_MACRO_TACTILE plus STYLE_GRAIN_HALATION but not STYLE_ANAMORPHIC. Mixing too many style blocks into one shot dilutes the read.

For lighting, name the time of day and direction. "Late afternoon raking light from frame right" is more reliable than "cinematic lighting".

Negative blocks compound. Start with NEG_AI_PLASTIC_SKIN + NEG_AI_COMPOSITION + NEG_AI_LIGHTING on every human shot; layer NEG_HUMAN_ANATOMY when needed.

Override these block bodies with your own language as you build a personal voice. The block names are conventions you can keep—the contents are yours to evolve.
