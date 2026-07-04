# Simple version bump script.
# Usage:
#   python extras/bump_version.py        # bumps patch
#   python extras/bump_version.py minor  # bumps minor
#   python extras/bump_version.py major  # bumps major

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
vfile = ROOT / 'VERSION'

if not vfile.exists():
    vfile.write_text('0.0.0')

ver = vfile.read_text().strip()
parts = [int(p) for p in ver.split('.')]

mode = sys.argv[1].lower() if len(sys.argv) > 1 else 'patch'
if mode == 'major':
    parts[0] += 1
    parts[1] = 0
    parts[2] = 0
elif mode == 'minor':
    parts[1] += 1
    parts[2] = 0
else:  # patch
    parts[2] += 1

new_ver = '.'.join(map(str, parts))
vfile.write_text(new_ver)
print(new_ver)