#!/usr/bin/env python3
import json
import sys
import pytest
import os
from pathlib import Path

def main():
    # Ensure the project root is on sys.path and cwd so `from app import ...` works
    project_root = Path(__file__).resolve().parents[1]
    os.chdir(project_root)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Run only the extract tests to check local extraction logic
    exit_code = pytest.main(["-q", "tests/test_extract.py"])
    passed = exit_code == 0
    result = {"passed": passed, "exit_code": exit_code}
    with open(".test_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f)

    # Print simple variable-like output that can be parsed by shell
    print(f"TESTS_PASSED={str(passed).lower()}")
    print(f"EXIT_CODE={exit_code}")

    # Propagate non-zero exit for CI or scripted usage
    if not passed:
        sys.exit(exit_code)

if __name__ == '__main__':
    main()
