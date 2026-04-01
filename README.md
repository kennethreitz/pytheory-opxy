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

## Getting the Presets ⬇️

1. Click this link: [**Download ZIP**](https://github.com/kennethreitz/pytheory-opxy/archive/refs/heads/main.zip) (~200 MB)
2. Your browser will download a file called `pytheory-opxy-main.zip`
3. Double-click the zip file to unzip it (on Mac it will unzip automatically)
4. You'll see a folder called `pytheory-opxy-main` — that's everything

---

## Installing on Your OP-XY

You'll need [**Field Kit**](https://teenage.engineering/apps/field-kit), a free app from Teenage Engineering for managing presets on your OP-XY.

1. Download and open **Field Kit** on your Mac
2. Plug your OP-XY into your Mac with a USB-C cable
3. Your OP-XY will show up in Field Kit — click on it
4. Open the **presets** folder on your device
5. From the `pytheory-opxy-main` folder you downloaded, drag these into the presets folder:
   - `opxy-samples/pytheory/` — all 69 instruments
   - `opxy-samples/pytheory-drums/` — all 12 drum kits
6. Done! The presets will show up on your OP-XY right away

## Installing on Your OP-1 / OP-1 Field

1. Plug your OP-1 into your computer with a USB cable
2. On the OP-1, go to **TE > USB Disk** to enter disk mode
3. Your OP-1 will show up as a drive on your computer (like a USB stick)
4. Open the `synth` > `user` folder on the OP-1 drive
5. From the `pytheory-opxy-main` folder you downloaded, open `op1-samples/pytheory/`
6. Copy all the `.wav` files into the OP-1's `synth/user/` folder
7. Eject the OP-1 drive and exit disk mode
8. Load the samples using the **Sampler** synth engine on the OP-1

---

## Instruments

69 multisampled instruments, each with 6 samples across the keyboard (C2, C3, C4, A4, C5, C6).
Sustained instruments (strings, winds, organ, pads) loop seamlessly while you hold a key
and release when you let go. Plucked and percussive instruments play through naturally.

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
  metal        14 sounds   tight kick/snare/hat + toms & cymbals
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

## For Developers

Want to regenerate the samples yourself or tweak the presets?

```
pip install pytheory numpy scipy
python generate.py                # all instruments
python generate.py piano sitar    # just specific ones
python generate.py --patch        # update patch.json only (no audio regen)
python generate_drums.py          # all drum kits
```

See [opxy-preset-notes.md](opxy-preset-notes.md) for detailed documentation on the OP-XY preset format — what we learned about loop behavior, region fields, envelope settings, and more.

See [CHANGELOG.md](CHANGELOG.md) for what's changed.

---

Built with [PyTheory](https://github.com/kennethreitz/pytheory) by [Kenneth Reitz](https://github.com/kennethreitz).
