"""离线验证示例附件和回归脚本；不能验证模型会自动触发 Skill。"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins/agent-workbench"
SCRIPT = PLUGIN / "skills/retrieval-regression/scripts/compare.py"


def run(candidate):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(ROOT / "fixtures/baseline.json"), str(candidate)],
        capture_output=True, text=True, check=False,
    )


def main():
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
    assert marketplace["plugins"][0]["name"] == manifest["name"]
    assert (ROOT / marketplace["plugins"][0]["source"]).resolve() == PLUGIN
    skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
    assert len(skills) == 2
    for skill in skills:
        content = skill.read_text()
        assert content.startswith("---\n") and "\ndescription: " in content
    assert (PLUGIN / "skills/evidence-brief/references/output-template.md").is_file()
    print("PASS plugin files and 2 skill entrypoints")
    good = run(ROOT / "fixtures/candidate.json")
    assert good.returncode == 0 and "regressions=none" in good.stdout
    print("PASS improved candidate accepted")
    bad = run(ROOT / "fixtures/regressed.json")
    assert bad.returncode == 1 and "regressions=q1" in bad.stdout
    print("PASS regression rejected despite equal total hits")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "invalid.json"
        for content in ['[{"case_id":"q1","hit":"false"}]', '[]', 'null',
                        '[{"case_id":"other","hit":true}]',
                        '[{"case_id":"q1","hit":true},{"case_id":"q1","hit":true}]']:
            path.write_text(content)
            assert run(path).returncode == 2
    print("PASS invalid inputs rejected")


if __name__ == "__main__":
    main()
