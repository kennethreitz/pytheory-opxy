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

OPXY_DIR = os.path.join(os.path.dirname(__file__), "opxy-samples", "pytheory")
OP1_DIR = os.path.join(os.path.dirname(__file__), "op1-samples", "pytheory")

# Instruments that should be monophonic/legato (not polyphonic)
MONO_INSTRUMENTS = {
    # Monophonic by nature
    "theremin", "flute", "clarinet", "oboe", "bassoon", "trumpet",
    "trombone", "french_horn", "tuba", "saxophone", "alto_sax",
    "tenor_sax", "bari_sax", "didgeridoo", "bagpipe",
    # Bass instruments — typically mono
    "bass_guitar", "upright_bass", "synth_bass", "acid_bass", "808_bass",
    "contrabass",
    # Lead synths
    "synth_lead", "vocal",
}

# Instruments that sound best with oneshot (short percussive, no sustain)
ONESHOT_INSTRUMENTS = {
    "marimba", "xylophone", "glockenspiel",
    "timpani", "kalimba", "steel_drum", "celesta", "music_box",
    "harp", "koto", "banjo", "mandolin", "mandola", "ukulele",
    "acoustic_guitar", "harpsichord",
}

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


def _region_playmode(instrument_name: str) -> str:
    """Return the OP-XY region playmode for an instrument."""
    if instrument_name in ONESHOT_INSTRUMENTS:
        return "oneshot"
    return "gate"


def build_regions(sample_files, instrument_name: str):
    """Build OP-XY multisampler regions from a list of (filename, midi_note, framecount).

    Key ranges are split at midpoints between adjacent sample points.
    """
    playmode = _region_playmode(instrument_name)
    regions = []
    for i, (filename, midi, framecount) in enumerate(sample_files):
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

        # Gate instruments loop so they sustain while held,
        # then the amp envelope release handles fade-out.
        loop = playmode == "gate"
        regions.append({
            "fade.in": 0,
            "fade.out": 0,
            "framecount": framecount,
            "hikey": hikey,
            "lokey": lokey,
            "loop.crossfade": 4410,  # ~100ms crossfade for smooth loop
            "loop.enabled": loop,
            "loop.end": framecount,
            "loop.onrelease": False,
            "loop.start": 0,
            "pan": 0,
            "pitch.keycenter": midi,
            "playmode": playmode,
            "reverse": False,
            "sample": filename,
            "sample.end": framecount,
            "transpose": 0,
            "tune": 0,
        })

    return regions


def _engine_playmode(instrument_name: str) -> str:
    """Return the OP-XY engine playmode for an instrument."""
    if instrument_name in MONO_INSTRUMENTS:
        return "mono"
    return "poly"


def make_patch_json(regions: list, instrument_name: str) -> dict:
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
            "playmode": _engine_playmode(instrument_name),
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
            "amp": {"attack": 0, "decay": 0, "release": 200, "sustain": 32767},
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

    regions = build_regions(sample_files, name)
    patch = make_patch_json(regions, name)

    with open(os.path.join(preset_dir, "patch.json"), "w") as f:
        json.dump(patch, f, indent=2)

    print(f"  {name:24s}  {len(SAMPLE_POINTS)} samples  ({total_kb:.0f} KB)")


def generate_op1_sample(name: str, output_dir: str):
    """Generate a single A4 WAV for OP-1 sampler."""
    samples = render_note(name, "A4")
    wav_path = os.path.join(output_dir, f"{name}.wav")
    save_wav(wav_path, samples)
    size_kb = os.path.getsize(wav_path) / 1024
    print(f"  {name:24s}  ({size_kb:.0f} KB)")


def main():
    instruments = sorted(INSTRUMENTS.keys())

    # OP-XY multisampled presets
    os.makedirs(OPXY_DIR, exist_ok=True)
    print(f"Generating {len(instruments)} OP-XY presets to {OPXY_DIR}/\n")

    for name in instruments:
        try:
            generate_preset(name, OPXY_DIR)
        except Exception as e:
            print(f"  {name:24s} FAILED: {e}")

    print(f"\nDone. {len(instruments)} OP-XY presets.\n")

    # OP-1 single samples
    os.makedirs(OP1_DIR, exist_ok=True)
    print(f"Generating {len(instruments)} OP-1 samples to {OP1_DIR}/\n")

    for name in instruments:
        try:
            generate_op1_sample(name, OP1_DIR)
        except Exception as e:
            print(f"  {name:24s} FAILED: {e}")

    print(f"\nDone. {len(instruments)} OP-1 samples.")


if __name__ == "__main__":
    main()
