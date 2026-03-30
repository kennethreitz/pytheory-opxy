"""Install PyTheory presets to a connected OP-XY or OP-1.

Usage:
    python install.py                  # auto-detect device
    python install.py /path/to/device  # specify mount point
"""

import os
import shutil
import sys

PRESET_DIR = os.path.join(os.path.dirname(__file__), "pytheory")

# Common mount points to search for OP-XY / OP-1
SEARCH_PATHS = [
    # macOS — FUSE / Android File Transfer mounts
    "/Volumes/OP-XY",
    "/Volumes/OP-Z",
    "/Volumes/OP-1",
    "/Volumes/OP1",
    # Linux — GVFS MTP mounts
    *sorted(
        (
            os.path.join("/run/user", uid, "gvfs", entry)
            for uid in os.listdir("/run/user") if uid.isdigit()
            for entry in os.listdir(os.path.join("/run/user", uid, "gvfs"))
            if "mtp" in entry.lower()
        )
        if os.path.isdir("/run/user")
        else []
    ),
    # Linux — common manual mount points
    "/mnt/op-xy",
    "/mnt/opxy",
    "/media/op-xy",
]


def find_device():
    """Try to auto-detect a mounted OP-XY or OP-1."""
    for path in SEARCH_PATHS:
        if os.path.isdir(path):
            return path

    # Check /Volumes for anything with OP in the name
    if os.path.isdir("/Volumes"):
        for name in os.listdir("/Volumes"):
            if "op" in name.lower() and os.path.isdir(os.path.join("/Volumes", name)):
                return os.path.join("/Volumes", name)

    return None


def install_opxy(device_root):
    """Copy .preset folders to /presets/pytheory/ on the device."""
    dest = os.path.join(device_root, "presets", "pytheory")
    os.makedirs(dest, exist_ok=True)

    presets = sorted(
        d for d in os.listdir(PRESET_DIR) if d.endswith(".preset")
    )

    print(f"Installing {len(presets)} presets to {dest}/\n")

    for name in presets:
        src = os.path.join(PRESET_DIR, name)
        dst = os.path.join(dest, name)

        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        label = name.replace(".preset", "")
        print(f"  {label}")

    print(f"\nDone. {len(presets)} presets installed to {dest}/")


def install_op1(device_root):
    """Copy .wav files to /synth/user/ on the device."""
    dest = os.path.join(device_root, "synth", "user")
    os.makedirs(dest, exist_ok=True)

    presets = sorted(
        d for d in os.listdir(PRESET_DIR) if d.endswith(".preset")
    )

    print(f"Installing {len(presets)} samples to {dest}/\n")

    for name in presets:
        src_dir = os.path.join(PRESET_DIR, name)
        for f in os.listdir(src_dir):
            if f.endswith(".wav"):
                src = os.path.join(src_dir, f)
                dst = os.path.join(dest, f)
                shutil.copy2(src, dst)
                label = name.replace(".preset", "")
                print(f"  {label}")

    print(f"\nDone. {len(presets)} samples installed to {dest}/")


def main():
    if len(sys.argv) > 1:
        device_root = sys.argv[1]
    else:
        device_root = find_device()

    if not device_root or not os.path.isdir(device_root):
        print("Could not find a mounted OP-XY or OP-1.")
        print("Usage: python install.py /path/to/device")
        sys.exit(1)

    print(f"Found device at {device_root}\n")

    # Detect device type by directory structure
    if os.path.isdir(os.path.join(device_root, "presets")):
        install_opxy(device_root)
    elif os.path.isdir(os.path.join(device_root, "synth")):
        install_op1(device_root)
    else:
        # Default to OP-XY style
        print("Unknown device layout — installing as OP-XY presets.")
        install_opxy(device_root)


if __name__ == "__main__":
    main()
