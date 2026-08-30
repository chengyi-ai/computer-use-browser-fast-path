#!/usr/bin/env python3
"""Validate the public Skill package without external dependencies."""

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "computer-use-browser-fast-path"
VERSION = "1.1.0"
SKILL_DIR = ROOT / "skills" / NAME
SKILL_FILE = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
VERSION_FILE = SKILL_DIR / "VERSION"
UPDATE_SCRIPT = SKILL_DIR / "scripts" / "check_update.py"


def main():
    errors = []
    required = [
        ROOT / "LICENSE",
        ROOT / "README.md",
        ROOT / "README_EN.md",
        ROOT / ".github" / "workflows" / "validate.yml",
        SKILL_FILE,
        OPENAI_YAML,
        VERSION_FILE,
        UPDATE_SCRIPT,
        SKILL_DIR / "references" / "fast-path-playbook.md",
        SKILL_DIR / "references" / "benchmark.md",
        SKILL_DIR / "references" / "douyin-image-post-prepublish.md",
        ROOT / "tests" / "test_check_update.py",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"缺少文件: {path.relative_to(ROOT)}")

    skill_text = SKILL_FILE.read_text(encoding="utf-8") if SKILL_FILE.is_file() else ""
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", skill_text, flags=re.DOTALL)
    if not frontmatter:
        errors.append("SKILL.md 缺少有效 YAML frontmatter")
    else:
        header = frontmatter.group(1)
        if not re.search(rf"^name:\s*{re.escape(NAME)}\s*$", header, re.MULTILINE):
            errors.append("SKILL.md name 不正确")
        if not re.search(r"^description:\s*\S.+$", header, re.MULTILINE):
            errors.append("SKILL.md description 不能为空")

    if VERSION_FILE.is_file() and VERSION_FILE.read_text(encoding="utf-8").strip() != VERSION:
        errors.append(f"VERSION 必须为 {VERSION}")

    yaml_text = OPENAI_YAML.read_text(encoding="utf-8") if OPENAI_YAML.is_file() else ""
    if f"${NAME}" not in yaml_text:
        errors.append("agents/openai.yaml default_prompt 未引用当前 Skill")

    for reference in (
        "references/fast-path-playbook.md",
        "references/benchmark.md",
        "references/douyin-image-post-prepublish.md",
    ):
        if reference not in skill_text:
            errors.append(f"SKILL.md 未链接参考文件: {reference}")

    public_text_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and path.suffix in {".md", ".py", ".yaml", ".yml", ""}
    ]
    local_path_marker = "/" + "Users/"
    for path in public_text_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if local_path_marker in text:
            errors.append(f"包含本机绝对路径: {path.relative_to(ROOT)}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            clean = target.split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / clean).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)} 链接不存在: {target}")

    if UPDATE_SCRIPT.is_file():
        try:
            compile(UPDATE_SCRIPT.read_text(encoding="utf-8"), str(UPDATE_SCRIPT), "exec")
        except SyntaxError as exc:
            errors.append(f"更新脚本语法错误: {exc}")

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Repository is valid: {NAME} v{VERSION}")


if __name__ == "__main__":
    main()
