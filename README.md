# pytheory-opxy

Synthesized instrument and drum presets for the **Teenage Engineering OP-XY** and **OP-1**, generated from [PyTheory](https://github.com/kennethreitz/pytheory).

## Quick Start

1. [Download the zip](https://github.com/kennethreitz/pytheory-opxy/archive/refs/heads/main.zip) of this repo.
2. Copy the folders to your device:

**OP-XY** — copy `opxy-samples/pytheory/` and `opxy-samples/drums/` into `/presets/` on the device.

**OP-1 / OP-1 Field** — copy the `.wav` files from `op1-samples/pytheory/` into `/synth/user/` on the device.

## What's Included

**69 instruments** — multisampled at 6 pitches (C2–C6 + A4) with per-instrument playmode (poly, mono, oneshot).

**12 drum kits** — standard, latin, metal, marching, tabla, dhol, mridangam, djembe, doumbek, cajón, world, effects.

## Regenerating

```
pip install pytheory numpy scipy
python generate.py
python generate_drums.py
```
