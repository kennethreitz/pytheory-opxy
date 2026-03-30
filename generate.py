"""Generate OP-XY multisampler .preset folders for every PyTheory instrument.

Each preset contains samples at C2, C3, C4, A4, C5, C6 with key ranges
split at the midpoints between samples. The OP-XY transposes from the
nearest sample when you play other keys.
"""

import json
import os
import wave

import numpy as np

from pytheory import Tone, Score
from pytheory.play import render_score, SAMPLE_RATE
from pytheory.rhythm import INSTRUMENTS, Duration

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pytheory")

# Sample points: (note_name, midi_number)
SAMPLE_POINTS = [
    ("C2", 36),
    ("C3", 48),
    ("C4", 60),
    ("A4", 69),
    ("C5", 72),
    ("C6", 84),
]


def render_note(instrument_name: str, note: str) -> np.ndarray:
    """Render a single note using the given instrument preset.

    Returns mono float32 numpy array.
    """
    score = Score("4/4", bpm=80)
    part = score.part("inst", instrument=instrument_name)
    part.add(Tone.from_string(note), Duration.WHOLE)

    buf = render_score(score)  # float32 stereo (N, 2)

    if buf.ndim == 2:
        mono = buf.mean(axis=1)
    else:
        mono = buf

    return mono.astype(np.float32)


def save_wav(path: str, samples: np.ndarray):
    """Save float32 mono samples as 16-bit 44100 Hz mono WAV."""
    peak = np.max(np.abs(samples))
    if peak > 0:
        samples = samples / peak
    pcm = (samples * 32767).astype(np.int16)

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())


def build_regions(sample_files):
    """Build OP-XY multisampler regions from a list of (filename, midi_note, framecount).

    Key ranges are split at midpoints between adjacent sample points.
    """
    regions = []
    for i, (filename, midi, framecount) in enumerate(sample_files):
        # Calculate key range: midpoint to previous, midpoint to next
        if i == 0:
            lokey = 0
        else:
            prev_midi = sample_files[i - 1][1]
            lokey = (prev_midi + midi) // 2 + 1

        if i == len(sample_files) - 1:
            hikey = 127
        else:
            next_midi = sample_files[i + 1][1]
            hikey = (midi + next_midi) // 2

        regions.append({
            "fade.in": 0,
            "fade.out": 0,
            "framecount": framecount,
            "hikey": hikey,
            "lokey": lokey,
            "loop.crossfade": 0,
            "loop.enabled": False,
            "loop.end": framecount,
            "loop.onrelease": False,
            "loop.start": 0,
            "pan": 0,
            "pitch.keycenter": midi,
            "playmode": "oneshot",
            "reverse": False,
            "sample": filename,
            "sample.end": framecount,
            "transpose": 0,
            "tune": 0,
        })

    return regions


def make_patch_json(regions: list) -> dict:
    """Build an OP-XY multisampler patch.json."""
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
        "regions": regions,
        "type": "multisampler",
        "version": 4,
    }


def generate_preset(name: str, output_dir: str):
    """Generate a multisampled .preset folder for the named instrument."""
    preset_dir = os.path.join(output_dir, f"{name}.preset")
    os.makedirs(preset_dir, exist_ok=True)

    sample_files = []
    total_kb = 0

    for note, midi in SAMPLE_POINTS:
        samples = render_note(name, note)
        framecount = len(samples)

        # OP-XY: filenames <=14 chars
        wav_name = f"{note.lower()}.wav"
        wav_path = os.path.join(preset_dir, wav_name)
        save_wav(wav_path, samples)

        sample_files.append((wav_name, midi, framecount))
        total_kb += os.path.getsize(wav_path) / 1024

    regions = build_regions(sample_files)
    patch = make_patch_json(regions)

    with open(os.path.join(preset_dir, "patch.json"), "w") as f:
        json.dump(patch, f, indent=2)

    print(f"  {name:24s}  {len(SAMPLE_POINTS)} samples  ({total_kb:.0f} KB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    instruments = sorted(INSTRUMENTS.keys())
    print(f"Generating {len(instruments)} multisampled OP-XY presets to {OUTPUT_DIR}/\n")

    for name in instruments:
        try:
            generate_preset(name, OUTPUT_DIR)
        except Exception as e:
            print(f"  {name:24s} FAILED: {e}")

    print(f"\nDone. {len(instruments)} presets in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
