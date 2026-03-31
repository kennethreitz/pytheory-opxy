"""Generate OP-XY multisampler .preset folders for every PyTheory instrument.

Each preset contains samples at C2, C3, C4, A4, C5, C6. Uses the real
OP-XY multisampler format with lokey=0 stacking and amp envelope for
sustain/release behavior.
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

# Instruments that should be monophonic (not polyphonic)
# Monophonic instruments (no polyphony, but no glide)
MONO_INSTRUMENTS = {
    # Wind (articulated, not sliding)
    "flute", "clarinet", "oboe", "bassoon", "trumpet",
    "trombone", "french_horn", "tuba", "saxophone", "alto_sax",
    "tenor_sax", "bari_sax",
    # Bass (fingered)
    "bass_guitar", "upright_bass", "synth_bass", "contrabass",
    # Solo strings
    "sitar",
    # Bellows
    "accordion",
}

# Legato instruments (mono + portamento glide)
LEGATO_INSTRUMENTS = {
    "theremin", "didgeridoo", "vocal", "acid_bass", "808_bass",
    "pedal_steel", "singing_bowl", "singing_bowl_ring",
    "harmonium", "bagpipe", "synth_lead",
}

# Instruments that need looping to sustain while held
# (continuous/bowed/blown sounds that don't naturally decay)
LOOP_INSTRUMENTS = {
    # Bowed strings
    "violin", "viola", "cello", "contrabass", "string_ensemble",
    # Wind/blown
    "theremin", "didgeridoo", "bagpipe", "pipe_organ", "organ",
    "harmonium", "accordion", "flute", "clarinet", "oboe", "bassoon",
    "trumpet", "trombone", "french_horn", "tuba", "brass_ensemble",
    "saxophone", "alto_sax", "tenor_sax", "bari_sax",
    # Sustained synths
    "synth_pad", "synth_lead", "synth_bass", "acid_bass", "808_bass",
    "choir", "vocal", "granular_pad", "granular_texture",
    # Resonant / sustained mallet
    "singing_bowl_ring", "vibraphone",
}

# Instruments that need longer samples (slow attack/decay/resonance)
LONG_SAMPLE_INSTRUMENTS = {
    # Long natural decay
    "singing_bowl", "singing_bowl_ring", "tubular_bells",
    "crotales", "tingsha", "steel_drum",
    # Slow pads / textures
    "granular_pad", "granular_texture", "synth_pad",
    "string_ensemble", "choir", "pipe_organ",
    # Resonant instruments
    "timpani", "vibraphone", "harp",
    "electric_piano", "wurlitzer", "pedal_steel",
}

EXCLUDED_INSTRUMENTS = set()

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
    Long-decay instruments get 8 seconds, others get 3.
    """
    if instrument_name in LONG_SAMPLE_INSTRUMENTS:
        bpm = 30  # 4 beats at 30 bpm = 8 seconds
    else:
        bpm = 80  # 4 beats at 80 bpm = 3 seconds

    score = Score("4/4", bpm=bpm)
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


def _find_zero_crossing(samples, target, direction=1):
    """Find the nearest positive-going zero crossing to target frame.

    Searches outward from target in the given direction.
    Returns the frame index where the waveform crosses from negative to positive.
    """
    n = len(samples)
    for offset in range(min(4410, n // 4)):  # search up to ~100ms
        idx = target + offset * direction
        if 0 < idx < n - 1:
            if samples[idx - 1] <= 0 < samples[idx]:
                return idx
    return target  # fallback


def build_regions(sample_files, instrument_name: str):
    """Build OP-XY sampler regions matching the factory preset format.

    Key ranges split at midpoints. Loop points snap to zero crossings
    for click-free looping.
    """
    should_loop = instrument_name in LOOP_INSTRUMENTS
    regions = []
    for i, (filename, midi, framecount, samples) in enumerate(sample_files):
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

        if should_loop:
            # Loop the sustain portion — skip attack, snap to zero crossings
            raw_start = framecount * 2 // 5   # ~40%
            raw_end = framecount * 4 // 5     # ~80%
            loop_start = _find_zero_crossing(samples, raw_start, direction=1)
            loop_end = _find_zero_crossing(samples, raw_end, direction=-1)
            # Crossfade proportional to loop length
            loop_len = max(1, loop_end - loop_start)
            crossfade = max(1, loop_len // 10)  # 10% of loop
        else:
            # Non-looping: loop near tail
            raw_start = framecount * 9 // 10
            loop_start = _find_zero_crossing(samples, raw_start, direction=1)
            loop_end = framecount
            crossfade = max(1, framecount // 100)

        regions.append({
            "framecount": framecount,
            "hikey": hikey,
            "lokey": lokey,
            "loop.crossfade": crossfade,
            "loop.end": loop_end,
            "loop.onrelease": True,
            "loop.start": loop_start,
            "pitch.keycenter": midi,
            "reverse": False,
            "sample": filename,
            "sample.end": framecount,
            "tune": 0,
        })

    return regions


def make_patch_json(regions: list, instrument_name: str) -> dict:
    """Build an OP-XY multisampler patch.json matching factory format."""
    if instrument_name in LEGATO_INSTRUMENTS:
        playmode = "mono"
        portamento = 8000  # smooth glide
    elif instrument_name in MONO_INSTRUMENTS:
        playmode = "mono"
        portamento = 0
    else:
        playmode = "poly"
        portamento = 0

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
            "playmode": playmode,
            "portamento.amount": portamento,
            "portamento.type": 32767,
            "transpose": 0,
            "tuning.root": 0,
            "tuning.scale": 0,
            "velocity.sensitivity": 26541,
            "volume": 20082,
            "width": 0,
        },
        "envelope": {
            "amp": {"attack": 0, "decay": 2457, "release": 2000, "sustain": 32767},
            "filter": {
                "attack": 0,
                "decay": 9471,
                "release": 0,
                "sustain": 32767,
            },
        },
        "fx": {
            "active": False,
            "params": [24002, 0, 0, 30719, 0, 32767, 0, 0],
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
        "type": "sampler",
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

        wav_name = f"{note.lower()}.wav"
        wav_path = os.path.join(preset_dir, wav_name)
        save_wav(wav_path, samples)

        sample_files.append((wav_name, midi, framecount, samples))
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
    instruments = sorted(k for k in INSTRUMENTS if k not in EXCLUDED_INSTRUMENTS)

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
