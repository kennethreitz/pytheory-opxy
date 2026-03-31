```
   ____  ____        _  ____  __
  / __ \/ __ \______| |/_/ / / /
 / /_/ / /_/ /______/>  </ /_/ /
 \____/ .___/      /_/|_|\__, /
     /_/   preset notes /____/
```

# OP-XY Preset Format Notes

Findings from reverse-engineering Teenage Engineering OP-XY factory presets
and community tools. Everything here was learned by examining real `.preset`
folders on the device via Field Kit.

---

## Preset Structure

A `.preset` is a folder containing:
- `patch.json` — metadata, engine settings, region mappings
- One or more `.wav` files — 16-bit mono, 44100 Hz

## Preset Types

There are three `"type"` values in `patch.json`:

### `"sampler"`

Used for **all pitched/melodic instruments** — both single-sample and multi-sample.
This is the correct type for instruments, not `"multisampler"`.

- Regions define key ranges with `lokey`/`hikey` splits
- `pitch.keycenter` tells the engine what note the sample is tuned to
- The engine transposes from the keycenter when you play other notes
- Factory presets use midpoint key splits (not `lokey: 0` stacking)

### `"multisampler"`

Found in some third-party presets (e.g. `asc multis` folder). Uses `loop.enabled`
field in regions (unlike `"sampler"` type). Relies on amp envelope for
sustain/release rather than `loop.onrelease`.

**Not recommended** — `"sampler"` type with multiple regions works better and
matches factory behavior.

### `"drum"`

Used for drum kits. 24 slots mapped to MIDI keys 53–76. Each region gets
`lokey == hikey` (one sample per key). Always `"playmode": "oneshot"` in regions.

---

## Region Fields

### Sampler regions

```json
{
  "framecount": 132300,
  "hikey": 60,
  "lokey": 43,
  "loop.crossfade": 1323,
  "loop.end": 105840,
  "loop.onrelease": true,
  "loop.start": 52920,
  "pitch.keycenter": 60,
  "reverse": false,
  "sample": "c4.wav",
  "sample.end": 132300,
  "tune": 0
}
```

**Important:** Sampler regions do NOT use `loop.enabled`. The presence of
`loop.enabled: true` causes the OP-XY to loop forever, ignoring key release.
Factory sampler presets only use `loop.onrelease`.

### Drum regions

```json
{
  "fade.in": 0,
  "fade.out": 0,
  "framecount": 22050,
  "hikey": 53,
  "lokey": 53,
  "pan": 0,
  "pitch.keycenter": 60,
  "playmode": "oneshot",
  "reverse": false,
  "sample": "kick.wav",
  "sample.end": 22050,
  "transpose": 0,
  "tune": 0
}
```

Drum regions have extra fields not present in sampler regions:
`fade.in`, `fade.out`, `pan`, `playmode`, `transpose`.

---

## Looping Behavior

```
  key down                              key up
  v                                     v
  |--attack--|-------sustain loop-------|--release--|
  |          |  loop.start → loop.end   |          |
  |          |  ↑___________________↓   |  fade    |
  |  play    |  |  loop.crossfade   |   |  out     |
  |  from 0  |  |___________________|   |          |
```

### `loop.onrelease: true` (sampler type)

This is the key field for sustain-then-release behavior:
- While key is held: sample plays, then loops between `loop.start` and `loop.end`
- On key release: loop stops, amp envelope release takes over

### `loop.onrelease: false`

Sample plays through once. Amp envelope handles everything.

### `loop.enabled` (multisampler type only)

Only used with `"type": "multisampler"`. When `true`, loops continuously
regardless of key state. **Do not use with `"sampler"` type** — it causes
notes to sustain forever.

### Loop Point Selection

For click-free looping, loop start and end should land on **positive-going
zero crossings** in the audio waveform. Searching outward from the target
position (~100ms search window) to find the nearest crossing eliminates
audible clicks at the loop boundary.

Factory presets typically:
- **Sustained sounds** (strings, organ): loop from ~20–40% to ~80% of the sample
- **Plucked/decaying sounds** (harp, piano): loop near the tail (~90%+), just
  enough to sustain if held very long
- **Crossfade**: proportional to loop length. Factory values range from 1 to 30000+

---

## Engine Settings

### `engine.playmode`

| Value | Behavior |
|-------|----------|
| `"poly"` | Multiple simultaneous notes (keys, pads, ensembles) |
| `"mono"` | Single voice, last-note priority (leads, bass, wind) |

### `engine.portamento.amount`

Glide between notes when `playmode` is `"mono"`. Range 0–32767.
Set to 0 for articulated mono (trumpet, flute). Set to ~8000 for
legato glide (theremin, pedal steel).

### Envelope values

All envelope parameters are 0–32767.

Factory amp envelopes vary widely:
- **Bright piano**: `attack: 0, decay: 31485, release: 11056, sustain: 32767`
- **Body movin bass**: `attack: 0, decay: 0, release: 25885, sustain: 32767`
- **Church organ**: `attack: 0, decay: 25067, release: 16382, sustain: 32767`

A release of ~2000 gives a quick cutoff. Higher values (10000+) give a
slow fade after key release.

### Volume

Factory presets typically use `volume: 18348–24901`. Default center is 16384.

---

## Drum Kit Layout

```
  ┌─────────────────────────────────────────────┐
  │  53 54 55 56 57 58 59 60 61 62 63 64 65 66 │
  │  KK KK SN SN RM CL TB SH CH CH OH CV LT RD │
  │                                             │
  │  67 68 69 70 71 72 73 74 75 76              │
  │  MT CR HT BL CL CH CB GU AX AX              │
  └─────────────────────────────────────────────┘
```

The standard OP-XY drum layout (from the community
[opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/) and factory Rytm kits):

```
53  Kick             61  Closed HH
54  Kick (alt)       62  Closed HH (alt)
55  Snare            63  Open HH
56  Snare (alt)      64  Clave
57  Rim              65  Low Tom
58  Clap             66  Ride
59  Tamb/Perc        67  Mid Tom
60  Shaker           68  Crash
                     69  Hi Tom
                     70  Triangle/Bell
                     71  Low Conga
                     72  High Conga
                     73  Cowbell
                     74  Guiro
                     75  Metal/Aux
                     76  Chi/Aux
```

### Drum engine settings

Factory kits vary between two approaches:

**Classix/Yamalog style**: `playmode: "mono"`, `octave: -1`, `transpose: 12`
**Stomp style**: `playmode: "poly"`, `octave: 0`, `transpose: 0`

The community drum tool uses the poly/0/0 approach.
Amp envelope for drums is typically `release: 0` or `release: 1000`.

---

## File Naming

- OP-XY filenames should be **14 characters or fewer**
- Factory samples use the pattern `unnamed-{note}-{velocity}.wav`
- Third-party samples use descriptive names (e.g. `C2_AmbientGuitar_SG.wav`)
- `.preset` folder names appear in the device browser as-is

---

## Tools

- [Field Kit](https://teenage.engineering/apps/field-kit) — TE's macOS app for managing OP-XY presets
- [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/) — community web tool for building drum kits
- [OP-PatchStudio](https://github.com/ish-/te-opxy-patchstudio) — community preset editor
- [teopxy](https://github.com/paul-sneddon/teopxy) — Python tool for converting OP-1 patches to OP-XY
