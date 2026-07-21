from __future__ import annotations

import importlib.util
import json
from pathlib import Path

CONTROL = Path(__file__).resolve().parents[2] / "workspace-control" / "scripts" / "v2_pipeline.py"
SPEC = importlib.util.spec_from_file_location("ronniecross_v2", CONTROL)
if not SPEC or not SPEC.loader:
    raise SystemExit(f"Cannot load V2 control module: {CONTROL}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ROOT = Path(__file__).resolve().parents[1]
result = MODULE.mirror_check(ROOT / "data" / "processed", ROOT / "src" / "content" / "posts")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["pass"] else 1)
