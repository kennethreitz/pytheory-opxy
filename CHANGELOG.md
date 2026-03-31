# Changelog

## 2026-03-31

- Uniform rendering: whole note at 100 bpm + 3 whole rests of tail, auto-trimmed to last audible frame
- No looping — amp envelope handles sustain/release entirely
- Per-instrument amp release: long (12000) for resonant sounds (piano, vibes, bells, plucked strings), short (2000) for everything else
- Per-instrument playmode:
  - Legato (mono + portamento): theremin, didgeridoo, vocal, acid_bass, 808_bass, pedal_steel, singing_bowls, harmonium, bagpipe, synth_lead
  - Mono (no glide): winds, brass, bass instruments, sitar, accordion
  - Poly: keys, strings, ensembles, pads, guitars
- Silence trimming with 5% fade-out — no more abrupt cutoffs
- Restored distortion guitars — fixed in PyTheory v0.40.4
- Matched standard OP-XY drum layout from community [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/)
- Single instrument generation: `python generate.py sitar`
- Removed install.py
- Added [opxy-preset-notes.md](opxy-preset-notes.md) documenting the OP-XY preset format

## 2026-03-30

- Initial release
- 69 multisampled instruments (6 samples each: C2, C3, C4, A4, C5, C6)
- 12 drum kits (standard, latin, metal, marching, tabla, dhol, mridangam, djembe, doumbek, cajon, world, effects)
- OP-1 single-sample WAVs
- Built with [PyTheory](https://github.com/kennethreitz/pytheory) v0.40.4
