"""Generate OP-XY drum .preset folders from PyTheory's drum synth engine.

Drum sounds are grouped into thematic kits. Each kit is an OP-XY drum
preset with up to 24 samples mapped to keys 53-76.
"""

import json
import os
import wave

import numpy as np

from pytheory.rhythm import DrumSound
from pytheory.play import _render_drum_hit, SAMPLE_RATE

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "opxy-samples", "drums")
HIT_DURATION = 0.5  # seconds per drum hit


# ── Drum kits: name -> list of (DrumSound, display_name) ─────────────────────

KITS = {
    "standard": [
        (DrumSound.KICK, "kick"),
        (DrumSound.SNARE, "snare"),
        (DrumSound.RIMSHOT, "rimshot"),
        (DrumSound.CLAP, "clap"),
        (DrumSound.CLOSED_HAT, "cl_hat"),
        (DrumSound.OPEN_HAT, "op_hat"),
        (DrumSound.PEDAL_HAT, "pd_hat"),
        (DrumSound.LOW_TOM, "lo_tom"),
        (DrumSound.MID_TOM, "mid_tom"),
        (DrumSound.HIGH_TOM, "hi_tom"),
        (DrumSound.CRASH, "crash"),
        (DrumSound.RIDE, "ride"),
        (DrumSound.RIDE_BELL, "ride_bell"),
        (DrumSound.COWBELL, "cowbell"),
        (DrumSound.CLAVE, "clave"),
        (DrumSound.SHAKER, "shaker"),
        (DrumSound.TAMBOURINE, "tamb"),
        (DrumSound.CONGA_HIGH, "conga_hi"),
        (DrumSound.CONGA_LOW, "conga_lo"),
        (DrumSound.BONGO_HIGH, "bongo_hi"),
        (DrumSound.BONGO_LOW, "bongo_lo"),
        (DrumSound.TIMBALE_HIGH, "timbal_hi"),
        (DrumSound.TIMBALE_LOW, "timbal_lo"),
        (DrumSound.GUIRO, "guiro"),
    ],
    "latin": [
        (DrumSound.KICK, "kick"),
        (DrumSound.SNARE, "snare"),
        (DrumSound.RIMSHOT, "rimshot"),
        (DrumSound.CLAP, "clap"),
        (DrumSound.CLOSED_HAT, "cl_hat"),
        (DrumSound.OPEN_HAT, "op_hat"),
        (DrumSound.CONGA_HIGH, "conga_hi"),
        (DrumSound.CONGA_LOW, "conga_lo"),
        (DrumSound.BONGO_HIGH, "bongo_hi"),
        (DrumSound.BONGO_LOW, "bongo_lo"),
        (DrumSound.TIMBALE_HIGH, "timbal_hi"),
        (DrumSound.TIMBALE_LOW, "timbal_lo"),
        (DrumSound.AGOGO_HIGH, "agogo_hi"),
        (DrumSound.AGOGO_LOW, "agogo_lo"),
        (DrumSound.GUIRO, "guiro"),
        (DrumSound.CLAVE, "clave"),
        (DrumSound.SHAKER, "shaker"),
        (DrumSound.TAMBOURINE, "tamb"),
        (DrumSound.COWBELL, "cowbell"),
        (DrumSound.CABASA, "cabasa"),
    ],
    "tabla": [
        (DrumSound.TABLA_NA, "na"),
        (DrumSound.TABLA_TIN, "tin"),
        (DrumSound.TABLA_GE, "ge"),
        (DrumSound.TABLA_DHA, "dha"),
        (DrumSound.TABLA_TIT, "tit"),
        (DrumSound.TABLA_KE, "ke"),
        (DrumSound.TABLA_GE_BEND, "ge_bend"),
    ],
    "dhol": [
        (DrumSound.DHOL_DAGGA, "dagga"),
        (DrumSound.DHOL_TILLI, "tilli"),
        (DrumSound.DHOL_BOTH, "both"),
        (DrumSound.DHOLAK_GE, "dholak_ge"),
        (DrumSound.DHOLAK_NA, "dholak_na"),
        (DrumSound.DHOLAK_TIT, "dholak_tit"),
    ],
    "mridangam": [
        (DrumSound.MRIDANGAM_THAM, "tham"),
        (DrumSound.MRIDANGAM_NAM, "nam"),
        (DrumSound.MRIDANGAM_DIN, "din"),
        (DrumSound.MRIDANGAM_THA, "tha"),
    ],
    "djembe": [
        (DrumSound.DJEMBE_BASS, "bass"),
        (DrumSound.DJEMBE_TONE, "tone"),
        (DrumSound.DJEMBE_SLAP, "slap"),
    ],
    "doumbek": [
        (DrumSound.DOUMBEK_DUM, "dum"),
        (DrumSound.DOUMBEK_TEK, "tek"),
        (DrumSound.DOUMBEK_KA, "ka"),
    ],
    "cajon": [
        (DrumSound.CAJON_BASS, "bass"),
        (DrumSound.CAJON_SLAP, "slap"),
        (DrumSound.CAJON_TAP, "tap"),
        (DrumSound.CAJON_SLAP_SNARE, "slap_snare"),
    ],
    "metal": [
        (DrumSound.METAL_KICK, "kick"),
        (DrumSound.METAL_SNARE, "snare"),
        (DrumSound.METAL_HAT, "hat"),
        (DrumSound.SNARE, "snare2"),
        (DrumSound.CLOSED_HAT, "cl_hat"),
        (DrumSound.OPEN_HAT, "op_hat"),
        (DrumSound.LOW_TOM, "lo_tom"),
        (DrumSound.MID_TOM, "mid_tom"),
        (DrumSound.HIGH_TOM, "hi_tom"),
        (DrumSound.CRASH, "crash"),
        (DrumSound.RIDE, "ride"),
        (DrumSound.RIDE_BELL, "ride_bell"),
    ],
    "marching": [
        (DrumSound.MARCH_SNARE, "snare"),
        (DrumSound.MARCH_RIMSHOT, "rimshot"),
        (DrumSound.MARCH_CLICK, "click"),
        (DrumSound.QUAD_1, "quad_1"),
        (DrumSound.QUAD_2, "quad_2"),
        (DrumSound.QUAD_3, "quad_3"),
        (DrumSound.QUAD_4, "quad_4"),
        (DrumSound.QUAD_SPOCK, "spock"),
        (DrumSound.BASS_1, "bass_1"),
        (DrumSound.BASS_2, "bass_2"),
        (DrumSound.BASS_3, "bass_3"),
        (DrumSound.BASS_4, "bass_4"),
        (DrumSound.BASS_5, "bass_5"),
        (DrumSound.CRASH, "crash"),
    ],
    "world": [
        (DrumSound.DJEMBE_BASS, "djembe_bas"),
        (DrumSound.DJEMBE_TONE, "djembe_ton"),
        (DrumSound.DJEMBE_SLAP, "djembe_slp"),
        (DrumSound.DOUMBEK_DUM, "doumbek_du"),
        (DrumSound.DOUMBEK_TEK, "doumbek_tk"),
        (DrumSound.DOUMBEK_KA, "doumbek_ka"),
        (DrumSound.CAJON_BASS, "cajon_bass"),
        (DrumSound.CAJON_SLAP, "cajon_slap"),
        (DrumSound.CAJON_TAP, "cajon_tap"),
        (DrumSound.FINGER_CYMBAL, "fngr_cymbl"),
        (DrumSound.CABASA, "cabasa"),
        (DrumSound.SHAKER, "shaker"),
        (DrumSound.RAINSTICK, "rainstick"),
        (DrumSound.OCEAN_DRUM, "ocean_drum"),
        (DrumSound.WIND_CHIMES, "wnd_chimes"),
    ],
    "effects": [
        (DrumSound.RAINSTICK, "rainstick"),
        (DrumSound.RAINSTICK_SLOW, "rain_slow"),
        (DrumSound.OCEAN_DRUM, "ocean_drum"),
        (DrumSound.CABASA, "cabasa"),
        (DrumSound.WIND_CHIMES, "wnd_chimes"),
        (DrumSound.FINGER_CYMBAL, "fngr_cymbl"),
    ],
}


def render_hit(sound: DrumSound) -> np.ndarray:
    """Render a single drum hit to a float32 mono array."""
    n_samples = int(SAMPLE_RATE * HIT_DURATION)
    return _render_drum_hit(sound.value, n_samples)


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


def make_drum_patch_json(regions: list) -> dict:
    """Build an OP-XY drum preset patch.json."""
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
            "amp": {"attack": 0, "decay": 0, "release": 500, "sustain": 32767},
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
        "type": "drum",
        "version": 4,
    }


def generate_kit(kit_name: str, sounds: list, output_dir: str):
    """Generate a single drum .preset folder."""
    preset_dir = os.path.join(output_dir, f"{kit_name}.preset")
    os.makedirs(preset_dir, exist_ok=True)

    regions = []
    total_kb = 0

    for i, (sound, name) in enumerate(sounds):
        key = 53 + i  # OP-XY drum keys start at 53

        samples = render_hit(sound)
        framecount = len(samples)

        wav_name = f"{name[:14]}.wav"
        wav_path = os.path.join(preset_dir, wav_name)
        save_wav(wav_path, samples)
        total_kb += os.path.getsize(wav_path) / 1024

        regions.append({
            "fade.in": 0,
            "fade.out": 0,
            "framecount": framecount,
            "hikey": key,
            "lokey": key,
            "pan": 0,
            "pitch.keycenter": 60,
            "playmode": "oneshot",
            "reverse": False,
            "sample": wav_name,
            "sample.end": framecount,
            "transpose": 0,
            "tune": 0,
        })

    patch = make_drum_patch_json(regions)
    with open(os.path.join(preset_dir, "patch.json"), "w") as f:
        json.dump(patch, f, indent=2)

    print(f"  {kit_name:16s}  {len(sounds):2d} sounds  ({total_kb:.0f} KB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Generating {len(KITS)} drum kits to {OUTPUT_DIR}/\n")

    for kit_name, sounds in sorted(KITS.items()):
        try:
            generate_kit(kit_name, sounds, OUTPUT_DIR)
        except Exception as e:
            print(f"  {kit_name:16s} FAILED: {e}")

    print(f"\nDone. {len(KITS)} drum kits in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
