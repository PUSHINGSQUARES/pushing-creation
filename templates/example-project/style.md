<!--
Template lifted from PUSHING FRAMES (github.com/PUSHINGSQUARES/pushing-frames).
Format must remain compatible — projects authored here open cleanly in PUSHING FRAMES.
-->
---
title: BMW M-Series Track Day — Worked Example
author: ari-leavesley
pack_version: '0.1'
template_id: bmw
---

<!--
This is a real working pack from a BMW M-Series customer experience
brief. Annotations explain why each block reads the way it does. Strip
the comments, keep the blocks; or rewrite the bodies entirely once
you've absorbed the pattern.

Ari's actual ari_master_pack.md is one giant STYLE_GUIDE block. This
template breaks it into named blocks so a new user sees how granular
mixing-and-matching works.
-->

<!--
WHY: this is the all-purpose base. Most BMW shots need the photoreal
anchor and the film-stock palette. The two ride together so we keep
them as one block.
-->
## STYLE_GUIDE
highly detailed photorealistic textures, cinematic lighting, 8k resolution. kodak vision3 50d and kodak vision color print 2383, high contrast, analogue interference, subtle halation on highlights, micro chromatic aberration, soft bloom, subtle film grain, high dynamic range, cinematic contrast, no text.

<!--
WHY: M-car colour identity is part of the brand brief. Naming the three
hero colours stops the model wandering off into generic black/silver
press-fleet defaults. Locked-livery rules belong in style, not action.
-->
## STYLE_LIVERY_HERO
nardo grey or sao paulo yellow or isle of man green or portimao blue—M-series livery colours readable, M-stripe along rocker if specified, BMW roundel readable on bonnet, never on boot, never wrong colour blend.

<!--
WHY: the track context is recurring. Heat haze, rumble strips, paddock
detail—calling these as a state block once stops you re-typing the
environment three times per scene.
-->
## STYLE_TRACK_CONTEXT
british race circuit context, painted kerb rumble strips at apex, heat haze rising off tarmac in distance, paddock garages and tyre walls in background, scattered cumulus overhead, road slightly damp from morning—not bluebird sunny, not raining.

<!--
WHY: anatomy negatives, lifted from the original BMW pack. Pinned out
because human shots in this project are critical—instructor, drivers,
crew. We want zero AI hand mishaps.
-->
## NEG_HUMAN
ugly, deformed hands, extra fingers, missing fingers, fused fingers, distorted fingers, bad anatomy, bad proportions, extra limbs, missing limbs, floating limbs, disconnected limbs, mutated hands and faces, mutation, disfigured, blurry, low quality, watermark, text, writing, signature, plastic skin, smooth skin, doll, mannequin, bad eyes, crossed eyes, asymmetric features, bad teeth, clothing glitches, merging clothes, clipping through car seat, impossible pose, supernatural.

<!--
WHY: car-specific failures. The model is most likely to break wheels
(extra/missing) and motion blur physics (smear instead of streak).
Lifted from the original.
-->
## NEG_CAR
deformed car, distorted geometry, extra wheels, missing wheels, bad proportions, ugly, blurry, low quality, watermark, text, writing, signature, logo glitches, bad motion blur physics, melted body panels, impossible reflections.

<!--
WHY: keep the influencer aesthetic away. BMW M is "premium performance"—
the brand pulls hard against soft-glowy-dreamy.
-->
## NEG_AESTHETIC
travel-influencer dreamy aesthetic, everything-golden filter, soft-glowy-everywhere, lifestyle-stock-photo polish, magazine-cover front-on hero, ambient-occlusion fake, ringlight beauty look.

# Notes

Three-act narrative arc—Act 1 paddock anticipation, Act 2 track action, Act 3 post-session payoff. Style blocks above stay consistent across all three; what changes is camera, lens, and lighting state per shot.

Lead every shot with "Shot on [camera] mounted on [rig]". State T-stop, shutter speed, ISO. For action work include fps explicitly so the motion blur reads (1/48 at 24fps for cinematic shutter angle, 1/1000 at 240fps for slow-motion).

When generating a driver POV shot from inside a helmet, explicitly state the camera is inside the helmet, dark interior padding framing the visor edge, looking out through the visor glass. Without this the model renders the helmet from outside.

Override STYLE_GUIDE per-shot only when you want a deliberate break—for example, the GoPro fender-mount shot wants the fish-eye action-cam look, not the Alexa cinema look.
