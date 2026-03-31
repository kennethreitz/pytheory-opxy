```
   ____  ____        _  ____  __
  / __ \/ __ \______| |/_/ / / /
 / /_/ / /_/ /______/>  </ /_/ /
 \____/ .___/      /_/|_|\__, /
     /_/   preset notes /____/
```

# OP-XY Preset Format Notes

Findings from reverse-engineering Teenage Engineering OP-XY factory presets,
the official TE docs, and community tools (OP-PatchStudio, opxy-drum-tool).
Everything here was learned the hard way.

---

## Preset Structure

A `.preset` is a folder containing:
- `patch.json` — metadata, engine settings, region mappings
- One or more `.wav` files — 16-bit mono, 44100 Hz

---

## The Three Sampler Types

From the [OP-XY docs](https://teenage.engineering/guides/op-xy/sample):

### `"sampler"` — One Shot Synth Sampler

**Single sample** pitched across the keyboard. The key you record on
becomes the reference pitch. The OP-XY transposes from there.

- Responds to key release (gate behavior)
- `loop.onrelease` controls whether looping continues after key up
- Does NOT use `loop.enabled` field
- Only one sample zone — additional regions are ignored

### `"multisampler"` — Multisampler

**Up to 24 samples** mapped across the keyboard in zones. Each zone has
its own sample and pitch reference. "Fills down" — pitches samples down
to cover gaps between zones.

- **Does NOT gate on key release** — samples play through to completion
- Amp envelope decay is the only way to shape note length
- Uses `lokey: 0` stacking (OP-XY picks the region with highest `hikey`
  that the played note falls under)
- Supports `loop.enabled` and `loop.onrelease` fields in regions
- `playmode` field is NOT used in regions (only in drum type)

### `"drum"` — Drum Sampler

**24 one-shot samples** mapped to individual keys 53–76. No pitch shifting.

- Each key triggers its own independent sample
- `playmode: "oneshot"` in each region
- Uses extra region fields: `fade.in`, `fade.out`, `pan`, `playmode`, `transpose`

---

## Key Limitation: Multisampler Has No Gate

This is the most important thing to understand. The `"multisampler"` type
**does not stop playback on key release**. The sample plays through
regardless of whether you're holding the key or not.

The `"sampler"` type does gate, but only supports a single sample.

**Workaround:** Use amp envelope `decay` to shape notes so they
naturally fade. The [OP-PatchStudio](https://github.com/ish-/te-opxy-patchstudio)
default envelope works well:

```json
"amp": {"attack": 0, "decay": 20295, "sustain": 14989, "release": 16383}
```

This makes notes hit at full volume, decay to ~46%, and hold there.

---

## Region Fields

### Multisampler regions

```json
{
  "framecount": 132300,
  "hikey": 54,
  "lokey": 0,
  "loop.crossfade": 0,
  "loop.enabled": false,
  "loop.end": 132300,
  "loop.onrelease": false,
  "loop.start": 0,
  "pitch.keycenter": 48,
  "reverse": false,
  "sample": "c3.wav",
  "sample.end": 132300,
  "tune": 0
}
```

**`loop.onrelease`** means "continue looping after key release" — the
opposite of what you might expect. Setting it to `true` makes notes
sustain forever. Leave it `false`.

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

### Multisampler play modes (from TE docs)

These are set via the device UI, not in `patch.json` regions:
- **Key** — sample plays while held (only works on device-created presets?)
- **Oneshot** — plays through regardless of key
- **Loop** — loops at end point
- **Mute group** — choke behavior

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

### Amp envelope

All parameters are 0–32767. Since multisampler doesn't gate:

- **`decay`** is the primary control for note shape
- **`sustain`** sets the held level (lower = notes fade more)
- **`release`** has minimal effect (no gate to trigger it)
- **`attack`** controls fade-in time

Recommended default (from OP-PatchStudio):
```
attack: 0, decay: 20295, sustain: 14989, release: 16383
```

### `octave`

Shifts the keyboard range. Use negative values for bass instruments:
- `-2` for didgeridoo, 808 bass
- `-1` for bass guitar, contrabass, tuba, timpani

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

Standard layout (from [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/)):

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

---

## File Naming

- OP-XY filenames should be **14 characters or fewer**
- Factory samples use the pattern `unnamed-{note}-{velocity}.wav`
- `.preset` folder names appear in the device browser as-is

---

## Tools

- [Field Kit](https://teenage.engineering/apps/field-kit) — TE's macOS app for managing OP-XY presets
- [opxy-drum-tool](https://buba447.github.io/opxy-drum-tool/) — community web tool for building drum kits
- [OP-PatchStudio](https://github.com/ish-/te-opxy-patchstudio) — community preset editor (best reference for multisampler format)
- [teopxy](https://github.com/paul-sneddon/teopxy) — Python tool for converting OP-1 patches to OP-XY
