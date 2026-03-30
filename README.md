```
                 __  __
    ____  __  __/ /_/ /_  ___  ____  _______  __      ____  ____  _  ____  __
   / __ \/ / / / __/ __ \/ _ \/ __ \/ ___/ / / /_____/ __ \/ __ \| |/_/ / / /
  / /_/ / /_/ / /_/ / / /  __/ /_/ / /  / /_/ /_____/ /_/ / /_/ />  </ /_/ /
 / .___/\__, /\__/_/ /_/\___/\____/_/   \__, /      \____/ .___/_/|_|\__, /
/_/    /____/                           /____/           /_/         /____/
```

Synthesized instrument and drum presets for the **Teenage Engineering OP-XY** and **OP-1**,
generated from [PyTheory](https://github.com/kennethreitz/pytheory)'s synthesis engine.

Every sound is rendered from scratch — no samples were harmed in the making of this repo.

---

## Quick Start

1. [**Download the zip**](https://github.com/kennethreitz/pytheory-opxy/archive/refs/heads/main.zip) (~130 MB)
2. Copy to your device:

| Device | What to copy | Where to put it |
|--------|-------------|-----------------|
| **OP-XY** | `opxy-samples/pytheory/` | `/presets/pytheory/` |
| **OP-XY** | `opxy-samples/pytheory-drums/` | `/presets/pytheory-drums/` |
| **OP-1 / OP-1 Field** | `op1-samples/pytheory/*.wav` | `/synth/user/` |

OP-XY users: [Field Kit](https://teenage.engineering/apps/field-kit) makes managing presets easy.

---

## Instruments

69 multisampled instruments, each with 6 samples across the keyboard (C2, C3, C4, A4, C5, C6).
Mono/poly playmode set per instrument.

```
  Keys         piano, electric_piano, wurlitzer, pipe_organ, organ,
               harpsichord, celesta, music_box

  Strings      violin, viola, cello, contrabass, string_ensemble

  Woodwinds    flute, clarinet, oboe, bassoon, saxophone,
               alto_sax, tenor_sax, bari_sax

  Brass        trumpet, trombone, french_horn, tuba, brass_ensemble

  Plucked      acoustic_guitar, electric_guitar, clean_guitar,
               crunch_guitar, distorted_guitar, orange_crunch,
               metal_guitar, bass_guitar, upright_bass, harp,
               sitar, pedal_steel, banjo, mandolin, mandola,
               ukulele, koto

  Mallet       marimba, vibraphone, xylophone, glockenspiel,
               tubular_bells, timpani, crotales, tingsha,
               singing_bowl, singing_bowl_ring, kalimba, steel_drum

  Synths       synth_lead, synth_pad, synth_bass, acid_bass,
               granular_pad, granular_texture, vocal, choir, 808_bass

  Other        theremin, harmonium, accordion, didgeridoo, bagpipe
```

## Drum Kits

12 drum kits, up to 24 hits each, mapped to OP-XY drum keys 53–76.

```
  standard     24 sounds   full GM kit
  latin        20 sounds   congas, bongos, timbales, agogo, guiro
  metal        12 sounds   tight kick/snare/hat + toms & cymbals
  marching     14 sounds   snare, quads, 5 bass drums, crash
  world        15 sounds   djembe, doumbek, cajon, rainstick
  tabla         7 sounds   na, tin, ge, dha, tit, ke, ge_bend
  dhol          6 sounds   dagga, tilli, both + dholak
  mridangam     4 sounds   tham, nam, din, tha
  djembe        3 sounds   bass, tone, slap
  doumbek       3 sounds   dum, tek, ka
  cajon         4 sounds   bass, slap, tap, slap_snare
  effects       6 sounds   rainstick, ocean drum, wind chimes
```

---

## Regenerating

```
pip install pytheory numpy scipy
python generate.py           # instruments
python generate_drums.py     # drum kits
```

---

Built with [PyTheory](https://github.com/kennethreitz/pytheory) by [Kenneth Reitz](https://github.com/kennethreitz).
