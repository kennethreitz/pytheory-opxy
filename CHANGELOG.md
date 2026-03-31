# Changelog

## 2026-03-31

- Restored distortion guitars (crunch, distorted, orange_crunch, metal) — fixed in PyTheory v0.40.4
- Refined per-instrument behavior:
  - Legato (mono + portamento): theremin, didgeridoo, vocal, acid_bass, 808_bass, pedal_steel, singing_bowls, harmonium, bagpipe, synth_lead
  - Mono (no glide): winds, brass, bass instruments, sitar, accordion
  - Looping: bowed strings, wind/brass, sustained synths, vibraphone, 808_bass
  - Long samples (8s): singing bowls, tubular bells, crotales, tingsha, vibraphone, harp, electric piano, wurlitzer, pedal steel, pads, choir, pipe organ, timpani, steel drum
- Matched standard OP-XY drum layout from community [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/)
- Matched drum engine settings to factory presets

## 2026-03-30

- Initial release
- 69 multisampled instruments (6 samples each: C2, C3, C4, A4, C5, C6)
- 12 drum kits (standard, latin, metal, marching, tabla, dhol, mridangam, djembe, doumbek, cajon, world, effects)
- OP-1 single-sample WAVs
- Preset format matched to OP-XY factory presets (`type: "sampler"`, `loop.onrelease: true`)
- Install script for auto-detecting OP-XY / OP-1
- Built with [PyTheory](https://github.com/kennethreitz/pytheory) v0.40.4
