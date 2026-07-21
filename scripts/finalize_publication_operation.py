from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

CONTROL = Path(__file__).resolve().parents[2] / "workspace-control" / "scripts" / "v2_pipeline.py"
SPEC = importlib.util.spec_from_file_location("ronniecross_v2", CONTROL)
if not SPEC or not SPEC.loader:
    raise SystemExit(f"Cannot load V2 control module: {CONTROL}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive publication-operation-result/v2 final status from evidence.")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--markdown")
    args = parser.parse_args()
    result = MODULE.finalize_result(Path(args.input), Path(args.output), Path(args.markdown) if args.markdown else None)
    print(result["final_status"])
    return 0 if result["final_status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
