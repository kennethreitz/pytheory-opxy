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

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "opxy-samples", "pytheory-drums")
HIT_DURATION = 0.5  # seconds per drum hit


# ── Drum kits: name -> list of (DrumSound, display_name) ─────────────────────

KITS = {
    # 808/909-style layout matching OP-XY factory kits (Rytm classic)
    # Kicks at bottom, snare/rim/clap, toms interleaved with hats, cymbals top
    "standard": [
        (DrumSound.KICK, "kick"),          # 53  kick
        (DrumSound.KICK, "kick2"),         # 54  kick variation
        (DrumSound.SNARE, "snare"),        # 55  snare
        (DrumSound.RIMSHOT, "rimshot"),    # 56  rimshot
        (DrumSound.CLAP, "clap"),          # 57  clap
        (DrumSound.COWBELL, "cowbell"),     # 58  cowbell
        (DrumSound.PEDAL_HAT, "pd_hat"),   # 59  pedal hat
        (DrumSound.LOW_TOM, "lo_tom"),     # 60  low tom
        (DrumSound.CLOSED_HAT, "cl_hat"),  # 61  closed hat
        (DrumSound.MID_TOM, "mid_tom"),    # 62  mid tom
        (DrumSound.OPEN_HAT, "op_hat"),    # 63  open hat
        (DrumSound.HIGH_TOM, "hi_tom"),    # 64  high tom
        (DrumSound.TAMBOURINE, "tamb"),    # 65  tambourine
        (DrumSound.RIDE, "ride"),          # 66  ride
        (DrumSound.RIDE_BELL, "ride_bell"),# 67  ride bell
        (DrumSound.CRASH, "crash"),        # 68  crash
        (DrumSound.SHAKER, "shaker"),      # 69  shaker
        (DrumSound.CLAVE, "clave"),        # 70  clave
        (DrumSound.CONGA_LOW, "conga_lo"), # 71  conga low
        (DrumSound.CONGA_HIGH, "conga_hi"),# 72  conga high
        (DrumSound.BONGO_LOW, "bongo_lo"), # 73  bongo low
        (DrumSound.BONGO_HIGH, "bongo_hi"),# 74  bongo high
        (DrumSound.TIMBALE_LOW, "timbal_lo"),# 75  timbale low
        (DrumSound.TIMBALE_HIGH, "timbal_hi"),# 76  timbale high
    ],
    "latin": [
        (DrumSound.KICK, "kick"),
        (DrumSound.RIMSHOT, "rimshot"),
        (DrumSound.SNARE, "snare"),
        (DrumSound.CLAP, "clap"),
        (DrumSound.CLOSED_HAT, "cl_hat"),
        (DrumSound.OPEN_HAT, "op_hat"),
        (DrumSound.CONGA_LOW, "conga_lo"),
        (DrumSound.CONGA_HIGH, "conga_hi"),
        (DrumSound.BONGO_LOW, "bongo_lo"),
        (DrumSound.BONGO_HIGH, "bongo_hi"),
        (DrumSound.TIMBALE_LOW, "timbal_lo"),
        (DrumSound.TIMBALE_HIGH, "timbal_hi"),
        (DrumSound.AGOGO_LOW, "agogo_lo"),
        (DrumSound.AGOGO_HIGH, "agogo_hi"),
        (DrumSound.COWBELL, "cowbell"),
        (DrumSound.CLAVE, "clave"),
        (DrumSound.GUIRO, "guiro"),
        (DrumSound.SHAKER, "shaker"),
        (DrumSound.TAMBOURINE, "tamb"),
        (DrumSound.CABASA, "cabasa"),
    ],
    # Tabla: bass (bayan) first, then treble (dayan), low to high
    "tabla": [
        (DrumSound.TABLA_GE, "ge"),
        (DrumSound.TABLA_GE_BEND, "ge_bend"),
        (DrumSound.TABLA_KE, "ke"),
        (DrumSound.TABLA_DHA, "dha"),
        (DrumSound.TABLA_NA, "na"),
        (DrumSound.TABLA_TIN, "tin"),
        (DrumSound.TABLA_TIT, "tit"),
    ],
    # Dhol/Dholak: bass side first, then treble
    "dhol": [
        (DrumSound.DHOL_DAGGA, "dagga"),
        (DrumSound.DHOL_BOTH, "both"),
        (DrumSound.DHOL_TILLI, "tilli"),
        (DrumSound.DHOLAK_GE, "dholak_ge"),
        (DrumSound.DHOLAK_NA, "dholak_na"),
        (DrumSound.DHOLAK_TIT, "dholak_tit"),
    ],
    # Mridangam: bass first, then treble
    "mridangam": [
        (DrumSound.MRIDANGAM_THAM, "tham"),
        (DrumSound.MRIDANGAM_THA, "tha"),
        (DrumSound.MRIDANGAM_DIN, "din"),
        (DrumSound.MRIDANGAM_NAM, "nam"),
    ],
    # Djembe: bass, tone, slap (low to high)
    "djembe": [
        (DrumSound.DJEMBE_BASS, "bass"),
        (DrumSound.DJEMBE_TONE, "tone"),
        (DrumSound.DJEMBE_SLAP, "slap"),
    ],
    # Doumbek: bass, tone, slap (low to high)
    "doumbek": [
        (DrumSound.DOUMBEK_DUM, "dum"),
        (DrumSound.DOUMBEK_TEK, "tek"),
        (DrumSound.DOUMBEK_KA, "ka"),
    ],
    # Cajón: bass, tap, slap, snare (low to high)
    "cajon": [
        (DrumSound.CAJON_BASS, "bass"),
        (DrumSound.CAJON_TAP, "tap"),
        (DrumSound.CAJON_SLAP, "slap"),
        (DrumSound.CAJON_SLAP_SNARE, "slap_snare"),
    ],
    # Metal: same 808 interleaved layout
    "metal": [
        (DrumSound.METAL_KICK, "kick"),
        (DrumSound.METAL_KICK, "kick2"),
        (DrumSound.METAL_SNARE, "snare"),
        (DrumSound.SNARE, "snare2"),
        (DrumSound.METAL_HAT, "hat"),
        (DrumSound.METAL_HAT, "hat2"),
        (DrumSound.LOW_TOM, "lo_tom"),
        (DrumSound.CLOSED_HAT, "cl_hat"),
        (DrumSound.MID_TOM, "mid_tom"),
        (DrumSound.OPEN_HAT, "op_hat"),
        (DrumSound.HIGH_TOM, "hi_tom"),
        (DrumSound.CRASH, "crash"),
        (DrumSound.RIDE, "ride"),
        (DrumSound.RIDE_BELL, "ride_bell"),
    ],
    # Marching: bass drums (low to high), snares, quads (low to high), crash
    "marching": [
        (DrumSound.BASS_5, "bass_5"),
        (DrumSound.BASS_4, "bass_4"),
        (DrumSound.BASS_3, "bass_3"),
        (DrumSound.BASS_2, "bass_2"),
        (DrumSound.BASS_1, "bass_1"),
        (DrumSound.MARCH_SNARE, "snare"),
        (DrumSound.MARCH_RIMSHOT, "rimshot"),
        (DrumSound.MARCH_CLICK, "click"),
        (DrumSound.QUAD_4, "quad_4"),
        (DrumSound.QUAD_3, "quad_3"),
        (DrumSound.QUAD_2, "quad_2"),
        (DrumSound.QUAD_1, "quad_1"),
        (DrumSound.QUAD_SPOCK, "spock"),
        (DrumSound.CRASH, "crash"),
    ],
    # World: hand drums (low to high), then aux percussion
    "world": [
        (DrumSound.DJEMBE_BASS, "djembe_bas"),
        (DrumSound.DJEMBE_TONE, "djembe_ton"),
        (DrumSound.DJEMBE_SLAP, "djembe_slp"),
        (DrumSound.DOUMBEK_DUM, "doumbek_du"),
        (DrumSound.DOUMBEK_TEK, "doumbek_tk"),
        (DrumSound.DOUMBEK_KA, "doumbek_ka"),
        (DrumSound.CAJON_BASS, "cajon_bass"),
        (DrumSound.CAJON_TAP, "cajon_tap"),
        (DrumSound.CAJON_SLAP, "cajon_slap"),
        (DrumSound.SHAKER, "shaker"),
        (DrumSound.CABASA, "cabasa"),
        (DrumSound.FINGER_CYMBAL, "fngr_cymbl"),
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
            "playmode": "mono",
            "portamento.amount": 128,
            "portamento.type": 32767,
            "transpose": 12,
            "tuning.root": 0,
            "tuning.scale": 3045,
            "velocity.sensitivity": 6879,
            "volume": 24901,
            "width": 0,
        },
        "envelope": {
            "amp": {"attack": 0, "decay": 0, "release": 0, "sustain": 32767},
            "filter": {
                "attack": 3932,
                "decay": 13167,
                "release": 9502,
                "sustain": 18062,
            },
        },
        "fx": {
            "active": False,
            "params": [6963, 16711, 10382, 5632, 0, 32767, 0, 0],
            "type": "z lowpass",
        },
        "lfo": {
            "active": False,
            "params": [9168, 6334, 23210, 29491, 0, 0, 0, 18186],
            "type": "random",
        },
        "octave": -1,
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
