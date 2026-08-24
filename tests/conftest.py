"""Make the sidecar importable under the name it uses internally.

Every module imports absolutely as `ipcha.*`, while the directory is named
`sidecar/` (the Dockerfile renames it on COPY). Aliasing the package in
sys.modules lets submodule imports resolve via the parent's __path__.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import sidecar  # noqa: E402

sys.modules.setdefault("ipcha", sidecar)
