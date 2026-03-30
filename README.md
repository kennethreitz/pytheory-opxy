# pytheory-opxy

A collection of 69 synthesized instrument presets for the **Teenage Engineering OP-XY** (and **OP-1/OP-1 Field**), generated from [PyTheory](https://github.com/kennethreitz/pytheory)'s instrument library.

Each preset is a single A4 (440 Hz) sample rendered through PyTheory's synthesis engine with the full effects chain (reverb, chorus, distortion, cabinet simulation, etc.) for each instrument. The OP-XY handles pitch transposition from this reference note across the keyboard.

## Presets

**Keys:** piano, electric_piano, wurlitzer, pipe_organ, organ, harpsichord, celesta, music_box

**Strings:** violin, viola, cello, contrabass, string_ensemble

**Woodwinds:** flute, clarinet, oboe, bassoon, saxophone, alto_sax, tenor_sax, bari_sax

**Brass:** trumpet, trombone, french_horn, tuba, brass_ensemble

**Plucked:** acoustic_guitar, electric_guitar, clean_guitar, crunch_guitar, distorted_guitar, orange_crunch, metal_guitar, bass_guitar, upright_bass, harp, sitar, pedal_steel, banjo, mandolin, mandola, ukulele, koto

**Percussion/Mallet:** marimba, vibraphone, xylophone, glockenspiel, tubular_bells, timpani, crotales, tingsha, singing_bowl, singing_bowl_ring, kalimba, steel_drum

**Synths:** synth_lead, synth_pad, synth_bass, acid_bass, granular_pad, granular_texture, vocal, choir, 808_bass

**Other:** theremin, harmonium, accordion, didgeridoo, bagpipe

## Format

Each `.preset` folder contains:
- A 16-bit mono WAV file (44100 Hz, ~3 seconds)
- A `patch.json` with `pitch.keycenter: 69` (MIDI A4)

**OP-XY:** Copy the `.preset` folders to `/presets/user/` via MTP.

**OP-1 / OP-1 Field:** The WAV files can be loaded directly into the OP-1's sampler engine. Import the `.wav` files from each preset folder into the OP-1's sample slots.

## Installation

### Automatic

Connect your OP-XY or OP-1 and run:

```
python install.py
```

Or specify the mount point directly:

```
python install.py /Volumes/OP-XY
```

The script auto-detects the device type and copies presets to the right location:
- **OP-XY** → `/presets/pytheory/` on the device
- **OP-1 / OP-1 Field** → `/synth/user/` on the device

### Manual

**OP-XY:** Copy the `pytheory/` folder into `/presets/` on the device (so presets live at `/presets/pytheory/`).

**OP-1 / OP-1 Field:** Copy the `.wav` files from each preset folder into `/synth/user/` on the device, then load them into the Sampler synth engine.

## Regenerating

Requires Python 3.10+ and [PyTheory](https://github.com/kennethreitz/pytheory):

```
pip install pytheory numpy scipy
python generate.py
```
