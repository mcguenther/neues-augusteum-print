#!/bin/bash
# Installiert die Python-Abhängigkeiten (generate.py, preview.py) beim Start
# einer Claude-Code-Cloud-Session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

# Schon alles da? Dann nichts tun (idempotent, schneller Start).
if python3 -c "import manifold3d, trimesh, shapely, numpy, scipy, lxml, networkx, matplotlib, PIL, pyproj, laspy, lazrs, cv2, numba, fast_simplification" 2>/dev/null; then
  echo "Python-Abhängigkeiten bereits installiert."
  exit 0
fi

python3 -m pip install --quiet --disable-pip-version-check --root-user-action=ignore -r requirements.txt
echo "Python-Abhängigkeiten installiert."
