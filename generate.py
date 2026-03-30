"""Generate OP-XY .preset folders for every PyTheory instrument.

Each preset contains a single A4 (440 Hz) sample and a patch.json
configured as a synth sampler with pitch.keycenter = 69 (MIDI A4).
The OP-XY transposes from this reference when you play other keys.
"""

import json
import os
import struct
import wave

import numpy as np

from pytheory import Tone, Score
from pytheory.play import render_score, SAMPLE_RATE
from pytheory.rhythm import INSTRUMENTS

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pytheory")
DURATION_MS = 3000  # 3 seconds per sample
NOTE = "A4"


def render_instrument(name: str) -> np.ndarray:
    """Render a single A4 note using the given instrument preset.

    Returns mono float32 numpy array.
    """
    score = Score("4/4", bpm=80)
    part = score.part("inst", instrument=name)
    # 3 seconds at 80 bpm = 4 beats
    from pytheory.rhythm import Duration
    part.add(Tone.from_string(NOTE), Duration.WHOLE)

    buf = render_score(score)  # float32 stereo (N, 2)

    # Mix to mono
    if buf.ndim == 2:
        mono = buf.mean(axis=1)
    else:
        mono = buf

    return mono.astype(np.float32)


def save_wav(path: str, samples: np.ndarray):
    """Save float32 mono samples as 16-bit 44100 Hz mono WAV."""
    peak = np.max(np.abs(samples))
    if peak > 0:
        samples = samples / peak  # normalize to -1..1
    pcm = (samples * 32767).astype(np.int16)

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def make_patch_json(sample_filename: str, framecount: int) -> dict:
    """Build an OP-XY synth sampler patch.json."""
    return {
        "engine": {
            "bendrange": 8191,
            "highpass": 0,
            "modulation": {
                "aftertouch": {"amount": 16383, "target": 0},
                "modwheel": {"amount": 16383, "target": 0},
                "pitchbend": {"amount": 16383, "target": 0},
                "velocity": {"amount": 16383, "target": 0},
            },
            "params": [16384, 16384, 16384, 16384, 16384, 16384, 16384, 16384],
            "playmode": "poly",
            "portamento.amount": 0,
            "portamento.type": 32767,
            "transpose": 0,
            "tuning.root": 0,
            "tuning.scale": 0,
            "velocity.sensitivity": 19660,
            "volume": 18348,
            "width": 0,
        },
        "envelope": {
            "amp": {"attack": 0, "decay": 0, "release": 1000, "sustain": 32767},
            "filter": {
                "attack": 0,
                "decay": 3276,
                "release": 23757,
                "sustain": 983,
            },
        },
        "fx": {
            "active": False,
            "params": [22014, 0, 30285, 11880, 0, 32767, 0, 0],
            "type": "ladder",
        },
        "lfo": {
            "active": False,
            "params": [6212, 16865, 18344, 16000, 0, 0, 0, 0],
            "type": "tremolo",
        },
        "octave": 0,
        "platform": "OP-XY",
        "regions": [
            {
                "fade.in": 0,
                "fade.out": 0,
                "framecount": framecount,
                "hikey": 127,
                "lokey": 0,
                "pan": 0,
                "pitch.keycenter": 69,  # MIDI A4
                "playmode": "oneshot",
                "reverse": False,
                "sample": sample_filename,
                "sample.end": framecount,
                "transpose": 0,
                "tune": 0,
            }
        ],
        "type": "sample",
        "version": 4,
    }


def generate_preset(name: str, output_dir: str):
    """Generate a single .preset folder for the named instrument."""
    preset_dir = os.path.join(output_dir, f"{name}.preset")
    os.makedirs(preset_dir, exist_ok=True)

    # Render audio
    samples = render_instrument(name)
    framecount = len(samples)

    # Truncate filename to 14 chars for OP-XY compatibility
    wav_name = f"{name[:14]}.wav"
    wav_path = os.path.join(preset_dir, wav_name)
    save_wav(wav_path, samples)

    # Write patch.json
    patch = make_patch_json(wav_name, framecount)
    patch_path = os.path.join(preset_dir, "patch.json")
    with open(patch_path, "w") as f:
        json.dump(patch, f, indent=2)

    size_kb = os.path.getsize(wav_path) / 1024
    print(f"  {name:24s} -> {wav_name:18s} ({framecount:>7d} frames, {size_kb:.0f} KB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    instruments = sorted(INSTRUMENTS.keys())
    print(f"Generating {len(instruments)} OP-XY presets to {OUTPUT_DIR}/\n")

    for name in instruments:
        try:
            generate_preset(name, OUTPUT_DIR)
        except Exception as e:
            print(f"  {name:24s} FAILED: {e}")

    print(f"\nDone. {len(instruments)} presets in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
