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
}

# Legato instruments (mono + portamento glide)
LEGATO_INSTRUMENTS = {
    "theremin", "didgeridoo", "vocal", "acid_bass", "808_bass",
    "pedal_steel",
    "synth_lead",
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
    "timpani", "vibraphone", "marimba", "xylophone",
    "glockenspiel", "celesta", "music_box", "kalimba", "harp",
    "sitar", "piano", "harpsichord",
    "electric_piano", "wurlitzer", "pedal_steel",
    # Sustained / legato — need length since we don't loop
    "theremin", "didgeridoo", "vocal", "harmonium", "bagpipe",
    "accordion", "organ", "808_bass", "acid_bass",
    "violin", "viola", "cello", "contrabass",
    "synth_lead", "synth_bass",
}


EXCLUDED_INSTRUMENTS = set()

# Default octave offset for instruments that sit in a low register
LOW_OCTAVE_INSTRUMENTS = {
    "didgeridoo": -2,
    "contrabass": -1,
    "upright_bass": -1,
    "bass_guitar": -2,
    "bari_sax": -1,
    "synth_bass": -1,
    "acid_bass": -1,
    "808_bass": -2,
    "cello": -1,
    "acoustic_guitar": -1,
    "electric_guitar": -1,
    "clean_guitar": -1,
    "crunch_guitar": -1,
    "distorted_guitar": -1,
    "orange_crunch": -1,
    "metal_guitar": -1,
    "glockenspiel": 1,
    "theremin": 1,
    "tingsha": 3,
    "vibraphone": 2,
    "viola": -1,
    "music_box": 1,
    "tuba": -1,
    "timpani": -1,
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
    Long-decay instruments get 8 seconds, others get 3.
    """
    bpm = 100  # whole note = 2.4s, plus tail rests for decay

    score = Score("4/4", bpm=bpm)
    if instrument_name == "808_bass":
        # Override: 808 needs a sustained sine, not a pluck
        part = score.part("inst", synth="sine", envelope="pad",
                          lowpass=200, sub_osc=0.5, distortion=0.4)
    else:
        part = score.part("inst", instrument=instrument_name)
    part.add(Tone.from_string(note), Duration.WHOLE)

    if instrument_name not in LOOP_INSTRUMENTS:
        # Non-looped: let the tail ring out for natural decay
        part.rest(Duration.WHOLE)
        part.rest(Duration.WHOLE)
        part.rest(Duration.WHOLE)

    buf = render_score(score)  # float32 stereo (N, 2)

    if buf.ndim == 2:
        mono = buf.mean(axis=1)
    else:
        mono = buf

    mono = mono.astype(np.float32)

    # Trim trailing silence (below -80 dB)
    threshold = 0.0001
    abs_mono = np.abs(mono)
    # Find last sample above threshold
    above = np.where(abs_mono > threshold)[0]
    if len(above) > 0:
        last_audible = above[-1]
        # Keep a short fade-out after last audible sample
        fade_len = min(4410, len(mono) - last_audible)  # ~100ms
        trim_point = min(last_audible + fade_len, len(mono))
        mono = mono[:trim_point]

    # Fade out the last 5% so the sample ends cleanly
    fade_len = max(1, len(mono) // 20)
    fade = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
    mono[-fade_len:] *= fade

    return mono


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


# Sustained instruments that should loop (gate on key release via loop.onrelease)
LOOP_INSTRUMENTS = {
    # Bowed strings
    "violin", "viola", "cello", "contrabass", "string_ensemble",
    # Wind/blown
    "flute", "clarinet", "oboe", "bassoon", "trumpet",
    "trombone", "french_horn", "tuba", "brass_ensemble",
    "bagpipe", "didgeridoo",
    # Keys/bellows
    "organ", "pipe_organ", "harmonium", "accordion",
    # Sustained synths
    "synth_pad", "synth_lead", "synth_bass", "acid_bass", "808_bass",
    "choir", "vocal", "granular_pad", "granular_texture",
    # Continuous
    "theremin", "singing_bowl_ring",
}


def _rms_at(samples, pos, window=2205):
    """RMS energy in a 50ms window around pos."""
    chunk = samples[max(0, pos - window // 2):pos + window // 2]
    if len(chunk) == 0:
        return 0.0
    return float(np.sqrt(np.mean(chunk ** 2)))


def _find_zero_crossing(samples, target, direction=1):
    """Find nearest positive-going zero crossing."""
    n = len(samples)
    for offset in range(4410):
        idx = target + offset * direction
        if 0 < idx < n - 1:
            if samples[idx - 1] <= 0 < samples[idx]:
                return idx
    return target


def _find_loop_points(samples):
    """Find RMS-matched, zero-crossing-snapped loop points in the sustain region.

    First finds where the actual signal is (above 25% of peak energy),
    then searches within that region for matching RMS levels.
    """
    fc = len(samples)
    window = 2205  # 50ms
    step = 441    # 10ms

    # Find peak RMS and the region where signal is above 25% of peak
    peak_rms = 0.0
    for pos in range(0, fc - window, step):
        r = _rms_at(samples, pos, window)
        if r > peak_rms:
            peak_rms = r

    if peak_rms < 0.01:
        return 0, fc, 0

    threshold = peak_rms * 0.25
    signal_start = 0
    signal_end = fc

    for pos in range(0, fc - window, step):
        if _rms_at(samples, pos, window) > threshold:
            signal_start = pos
            break

    for pos in range(fc - window, 0, -step):
        if _rms_at(samples, pos, window) > threshold:
            signal_end = pos
            break

    # Search within the signal region, skip the first 150ms (attack)
    search_start = max(signal_start + int(SAMPLE_RATE * 0.15), int(SAMPLE_RATE * 0.15))
    search_end = signal_end

    if search_end - search_start < SAMPLE_RATE // 2:
        return 0, fc, 0

    min_loop = SAMPLE_RATE // 2  # minimum 0.5s loop

    best_diff = 999.0
    best_pair = (search_start, search_end)

    for s in range(search_start, (search_start + search_end) // 2, step):
        s_rms = _rms_at(samples, s)
        if s_rms < threshold:
            continue
        for e in range(search_end, (search_start + search_end) // 2, -step):
            e_rms = _rms_at(samples, e)
            if e_rms < threshold:
                continue
            diff = abs(s_rms - e_rms)
            if diff < best_diff and (e - s) > min_loop:
                best_diff = diff
                best_pair = (s, e)

    s, e = best_pair
    s = _find_zero_crossing(samples, s, 1)
    e = _find_zero_crossing(samples, e, -1)
    crossfade = (e - s) // 3  # 33% of loop length

    return s, e, crossfade


def build_regions(sample_files, instrument_name: str):
    """Build OP-XY multisampler regions.

    Uses lokey=0 stacking. Sustained instruments get RMS-matched loop
    points with loop.onrelease for gate behavior.
    """
    should_loop = instrument_name in LOOP_INSTRUMENTS
    regions = []
    for i, (filename, midi, framecount, *_rest) in enumerate(sample_files):
        if i == len(sample_files) - 1:
            hikey = 127
        else:
            next_midi = sample_files[i + 1][1]
            hikey = (midi + next_midi) // 2

        if should_loop and len(_rest) > 0:
            samples = _rest[0]
            loop_start, loop_end, crossfade = _find_loop_points(samples)
            region_loop = {
                "loop.crossfade": crossfade,
                "loop.end": loop_end,
                "loop.onrelease": True,
                "loop.start": loop_start,
            }
        else:
            # Non-looped: loop.enabled=false, like factory ambguitar
            region_loop = {
                "loop.crossfade": 0,
                "loop.enabled": False,
                "loop.end": framecount,
                "loop.onrelease": False,
                "loop.start": 0,
            }

        regions.append({
            "framecount": framecount,
            "hikey": hikey,
            "lokey": 0,
            **region_loop,
            "pitch.keycenter": midi,
            "reverse": False,
            "sample": filename,
            "sample.end": framecount,
            "tune": 0,
        })

    return regions


def _amp_envelope(instrument_name: str) -> dict:
    """Return amp envelope."""
    if instrument_name in LOOP_INSTRUMENTS:
        # Looping instruments: full sustain, release fades on key up
        return {"attack": 0, "decay": 2457, "release": 14395, "sustain": 32767}
    else:
        # Non-looping: PatchStudio default decay envelope
        return {"attack": 0, "decay": 20295, "release": 16383, "sustain": 14989}


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
            "amp": _amp_envelope(instrument_name),
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
        "octave": LOW_OCTAVE_INSTRUMENTS.get(instrument_name, 0),
        "platform": "OP-XY",
        "regions": regions,
        "type": "multisampler",
        "version": 4,
    }


def update_patch(name: str, output_dir: str):
    """Update only the patch.json for an existing preset (no audio regen).

    Reads WAV data for loop point analysis on sustained instruments.
    """
    preset_dir = os.path.join(output_dir, f"{name}.preset")
    if not os.path.isdir(preset_dir):
        print(f"  {name:24s}  SKIP (no preset folder)", flush=True)
        return

    sample_files = []
    for note, midi in SAMPLE_POINTS:
        wav_name = f"{note.lower()}.wav"
        wav_path = os.path.join(preset_dir, wav_name)
        if not os.path.exists(wav_path):
            print(f"  {name:24s}  SKIP (missing {wav_name})", flush=True)
            return
        with wave.open(wav_path, "r") as wf:
            framecount = wf.getnframes()
            raw = wf.readframes(framecount)
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767
        sample_files.append((wav_name, midi, framecount, samples))

    regions = build_regions(sample_files, name)
    patch = make_patch_json(regions, name)

    with open(os.path.join(preset_dir, "patch.json"), "w") as f:
        json.dump(patch, f, indent=2)

    looped = " (looped)" if name in LOOP_INSTRUMENTS else ""
    print(f"  {name:24s}  patch.json updated{looped}", flush=True)


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

    print(f"  {name:24s}  {len(SAMPLE_POINTS)} samples  ({total_kb:.0f} KB)", flush=True)


def generate_op1_sample(name: str, output_dir: str):
    """Generate a single A4 WAV for OP-1 sampler."""
    samples = render_note(name, "A4")
    wav_path = os.path.join(output_dir, f"{name}.wav")
    save_wav(wav_path, samples)
    size_kb = os.path.getsize(wav_path) / 1024
    print(f"  {name:24s}  ({size_kb:.0f} KB)", flush=True)


def main():
    import sys
    all_instruments = sorted(k for k in INSTRUMENTS if k not in EXCLUDED_INSTRUMENTS)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    patch_only = "--patch" in sys.argv

    if args:
        instruments = [name for name in args if name in INSTRUMENTS]
        if not instruments:
            print(f"Unknown instrument(s): {args}")
            print(f"Available: {', '.join(all_instruments)}")
            sys.exit(1)
    else:
        instruments = all_instruments

    # OP-XY multisampled presets
    os.makedirs(OPXY_DIR, exist_ok=True)

    if patch_only:
        print(f"Updating {len(instruments)} patch.json files in {OPXY_DIR}/\n")
        for name in instruments:
            try:
                update_patch(name, OPXY_DIR)
            except Exception as e:
                print(f"  {name:24s} FAILED: {e}")
        print(f"\nDone. {len(instruments)} patches updated.")
        return

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
