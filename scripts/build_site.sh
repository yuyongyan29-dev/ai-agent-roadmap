#!/usr/bin/env bash
# 把仓库里的 Markdown 收集到 _site_src/ 供 mkdocs 构建。
# 为什么要拷一份：mkdocs 不允许 docs_dir 是仓库根目录（那里放着 mkdocs.yml 本身）。
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf _site_src
mkdir -p _site_src

# 根目录的文档。README 改名 index，成为站点首页
cp README.md _site_src/index.md
for f in 从这里开始.md 项目结构.md 扩展模块-B.md CONTRIBUTING.md; do
  [ -f "$f" ] && cp "$f" _site_src/
done
cp LICENSE _site_src/LICENSE.md

# 目录整体拷贝
cp -R units templates docs _site_src/
mkdir -p _site_src/logs && cp logs/README.md _site_src/logs/

echo "已生成 _site_src/，共 $(find _site_src -name '*.md' | wc -l | tr -d ' ') 个页面"
