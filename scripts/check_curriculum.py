#!/usr/bin/env python3
"""检查单元、阶段目录、网站导航和逐周课时是否一致。仅使用标准库。"""

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    errors = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    units = {}
    stage_totals = {}
    for stage in sorted((ROOT / "units").iterdir()):
        if not stage.is_dir():
            continue
        readme = (stage / "README.md").read_text()
        rows = re.findall(r"\| \[(U\d+\.\d+)[^\]]*\]\(([^)]+)\) \| (\d+)h \|", readme)
        listed = [uid for uid, _, _ in rows]
        actual = {p.name.split("-")[0]: p for p in stage.glob("U*.md")}
        check(len(listed) == len(set(listed)), f"{stage.name}: 单元目录重复")
        check(set(listed) == set(actual), f"{stage.name}: 文件与阶段目录不一致")
        for uid, name, hours in rows:
            path = stage / name
            check(path.is_file(), f"{uid}: 目录链接不存在 {name}")
            if not path.is_file():
                continue
            heading = path.read_text().splitlines()[0]
            match = re.fullmatch(r"# (U\d+\.\d+) · .+（(\d+) 小时）", heading)
            check(bool(match), f"{uid}: 标题格式错误")
            if match:
                check(match[1] == uid and int(match[2]) == int(hours), f"{uid}: 标题与目录课时不一致")
            units[uid] = int(hours)
        total = sum(int(h) for _, _, h in rows) + (6 if stage.name == "s0" else 0)
        stage_totals[stage.name.upper()] = total
        check(f"，{total} 小时）" in readme.splitlines()[0], f"{stage.name}: 阶段总课时错误")

    config = (ROOT / "mkdocs.yml").read_text()
    nav_paths = re.findall(r": (units/s\d+/U[^\n]+\.md)\s*$", config, re.M)
    actual_paths = {str(p.relative_to(ROOT)) for p in (ROOT / "units").glob("s*/U*.md")}
    check(set(nav_paths) == actual_paths and len(nav_paths) == len(actual_paths), "网站单元导航缺失或重复")

    weeks = (ROOT / "docs/周计划.md").read_text()
    scheduled = Counter()
    spans = defaultdict(list)
    week_ids = []
    scheduled_total = 0
    for line in weeks.splitlines():
        if not re.match(r"\| W\d+ \|", line):
            continue
        fields = [f.strip() for f in line.split("|")[1:-1]]
        week = int(fields[0][1:])
        entries = re.findall(r"(U\d+\.\d+|M0收尾)\((\d+)\)", fields[2])
        total = sum(int(h) for _, h in entries)
        check(0 < total <= 16, f"W{week}: 学习课时 {total} 超出范围")
        check(fields[3] == str(total), f"W{week}: 本周合计错误")
        expected_stages = []
        for uid, hours in entries:
            scheduled[uid] += int(hours)
            stage = "S0" if uid == "M0收尾" else "S" + uid[1]
            spans[stage].append(week)
            if stage not in expected_stages:
                expected_stages.append(stage)
        check(fields[1] == " / ".join(expected_stages), f"W{week}: 阶段标记不一致")
        week_ids.append(week)
        scheduled_total += total
    check(week_ids == list(range(1, 40)), "周计划必须连续覆盖 W1–W39")
    check(scheduled == Counter({**units, "M0收尾": 6}), "周计划累计课时与单元不一致")
    check(scheduled_total == 622, f"总课时应为 622，当前 {scheduled_total}")

    root_readme = (ROOT / "README.md").read_text()
    for stage, total in stage_totals.items():
        if not spans[stage]:
            errors.append(f"{stage}: 未安排周次")
            continue
        period = f"W{min(spans[stage])}–W{max(spans[stage])}"
        check(bool(re.search(rf"\| {stage} \|[^\n]*\| {period} \| {total}h \|", root_readme)), f"{stage}: 根目录时长或周次错误")
        heading = (ROOT / "units" / stage.lower() / "README.md").read_text().splitlines()[0]
        check(period in heading, f"{stage}: 阶段标题周次错误")
    check(f"{len(units)} 个单元" in root_readme, "README 单元总数错误")
    check(f"{len(units)} 个单元" in config, "站点描述单元总数错误")
    check("※" not in weeks and "另 3 个在写" not in root_readme, "仍有未完成标记")

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(units)} units, {sum(units.values())}h + M0 6h = {scheduled_total}h, 39 weeks <= 16h")


if __name__ == "__main__":
    main()
