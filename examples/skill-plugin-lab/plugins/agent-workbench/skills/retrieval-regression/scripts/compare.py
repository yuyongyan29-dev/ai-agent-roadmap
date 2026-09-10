"""比较相同 case 集的布尔命中结果；不调用模型。"""

import json
import sys
from pathlib import Path


def read_cases(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must be a non-empty list")
    cases = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each case must be an object")
        case_id, hit = row.get("case_id"), row.get("hit")
        if not isinstance(case_id, str) or not case_id or type(hit) is not bool:
            raise ValueError("case_id must be non-empty and hit must be bool")
        if case_id in cases:
            raise ValueError("duplicate case_id")
        cases[case_id] = hit
    return cases


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError("usage: compare.py BASELINE CANDIDATE")
        baseline, candidate = map(read_cases, sys.argv[1:])
        if baseline.keys() != candidate.keys():
            raise ValueError("case sets differ")
    except (ValueError, OSError) as exc:
        print(f"INVALID: {exc}")
        return 2
    regressions = sorted(k for k in baseline if baseline[k] and not candidate[k])
    print(f"baseline_hits={sum(baseline.values())}/{len(baseline)}")
    print(f"candidate_hits={sum(candidate.values())}/{len(candidate)}")
    print("regressions=" + (",".join(regressions) or "none"))
    return int(bool(regressions))


if __name__ == "__main__":
    sys.exit(main())
