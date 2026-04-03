# Changelog

## 2026-04-02

- 14 new instruments: analog_bass, analog_pad, drift_saw, drift_square, mellotron, mellotron_choir, mellotron_flute, mellotron_strings, ring_mod_bell, ring_mod_metallic, sync_lead, sync_lead_bright, wavefold_gnarly, wavefold_warm
- 83 total instruments (up from 69)
- Categorized all new instruments into metadata sets (mono/legato/loop/long_sample/octave offset)
- Upgraded to PyTheory v0.40.9 (local editable install via uv)

## 2026-04-01

- Looped instruments rendered without reverb tail — just clean sustain (2.4s)
- Loop analysis constrained to signal body (>25% peak RMS) to avoid looping silence
- Restored saxophones (saxophone, alto_sax, tenor_sax, bari_sax)
- Octave adjustments: bari_sax -1, bass_guitar -2, cello -1, viola -1, all guitars -1, glockenspiel +1, music_box +1, theremin +1, vibraphone +2, tingsha +3
- Sitar and singing bowls back to poly
- 808_bass override: sustained sine + pad envelope instead of pytheory's pluck
- Upgraded to PyTheory v0.40.6

## 2026-03-31

- Switched to `"multisampler"` type (TE docs: "sampler" = single sample, "multisampler" = up to 24 zones)
- RMS-matched looping for sustained instruments — loop points found by analyzing audio energy to match levels at both boundaries, snapped to zero crossings, with 33% crossfade
- Non-looped instruments explicitly set `loop.enabled: false` — without this the OP-XY loops the full sample
- Two amp envelopes: sustained (full sustain + release for gate) and non-looped (PatchStudio decay envelope)
- Per-instrument playmode:
  - Legato (mono + portamento): theremin, didgeridoo, vocal, acid_bass, 808_bass, pedal_steel, singing_bowls, synth_lead
  - Mono (no glide): winds, brass, bass instruments, sitar
  - Poly: keys, strings, ensembles, pads, guitars
- Silence trimming with 5% fade-out
- Matched standard OP-XY drum layout from community [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/)
- Single instrument generation: `python generate.py sitar`
- Patch-only updates: `python generate.py --patch`
- Added [opxy-preset-notes.md](opxy-preset-notes.md) documenting the OP-XY preset format

## 2026-03-30

- Initial release
- 69 multisampled instruments (6 samples each: C2, C3, C4, A4, C5, C6)
- 12 drum kits (standard, latin, metal, marching, tabla, dhol, mridangam, djembe, doumbek, cajon, world, effects)
- OP-1 single-sample WAVs
- Built with [PyTheory](https://github.com/kennethreitz/pytheory) v0.40.4
