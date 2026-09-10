#!/usr/bin/env python3
"""把一个阶段的 README 和全部单元合并成一份 Markdown，供导入飞书 / Notion。

用法：
    python3 scripts/build_stage_doc.py s0                 # 输出到 _stage_s0.md
    python3 scripts/build_stage_doc.py s0 -o out.md
    python3 scripts/build_stage_doc.py s0 --plain         # 不做飞书专用转换，给 Notion 等用

飞书模式（默认）做两件事：
1. 文件开头加 <title>，飞书全文替换时需要它
2. `- [ ] xxx` 转成飞书原生勾选框 <checkbox>。飞书的 Markdown 导入会转义勾选框
   里的行内标签，所以勾选框内的加粗和行内代码会降级成纯文本
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def unit_number(path: Path) -> int:
    """从 U0.10-xxx.md 里取出 10，用来按数字而不是字典序排序。"""
    m = re.search(r"U\d+\.(\d+)", path.name)
    return int(m.group(1)) if m else -1


def stage_files(stage: str) -> list[Path]:
    d = ROOT / "units" / stage
    if not d.is_dir():
        sys.exit(f"找不到阶段目录：{d}")
    units = sorted(d.glob("U*.md"), key=unit_number)
    return [d / "README.md", *units]


def plain_text(text: str) -> str:
    """去掉行内 Markdown 标记。飞书勾选框里不认这些。"""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return text


def convert_checkboxes(md: str) -> str:
    """代码块外的任务列表项转成飞书 <checkbox>。"""
    out, in_fence = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        m = None if in_fence else re.match(r"^(\s*)- \[( |x)\] (.*)$", line)
        if m:
            done = "true" if m.group(2) == "x" else "false"
            out.append(f'{m.group(1)}<checkbox done="{done}">{plain_text(m.group(3))}</checkbox>')
        else:
            out.append(line)
    return "\n".join(out)


def stage_title(readme: Path) -> str:
    first = readme.read_text(encoding="utf-8").splitlines()[0]
    return first.lstrip("# ").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", help="阶段目录名，如 s0")
    ap.add_argument("-o", "--output", help="输出文件，默认 _stage_<阶段>.md")
    ap.add_argument("--plain", action="store_true", help="不做飞书专用转换")
    args = ap.parse_args()

    files = stage_files(args.stage)
    parts: list[str] = []
    if not args.plain:
        parts += [f"<title>{stage_title(files[0])}</title>", ""]
    for f in files:
        body = f.read_text(encoding="utf-8").rstrip()
        parts.append(body if args.plain else convert_checkboxes(body))
        parts.append("\n---\n")

    out = Path(args.output) if args.output else ROOT / f"_stage_{args.stage}.md"
    doc = "\n".join(parts)
    out.write_text(doc, encoding="utf-8")
    print(f"写入 {out}（{len(files)} 个文件，{len(doc):,} 字符）")


if __name__ == "__main__":
    main()
