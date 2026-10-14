#!/usr/bin/env python3
"""Validate the public Skill package and the maintenance tooling without external dependencies."""

import json
import py_compile
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "computer-use-browser-fast-path"
VERSION = "1.1.1"
SKILL_DIR = ROOT / "skills" / NAME
SKILL_FILE = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
VERSION_FILE = SKILL_DIR / "VERSION"
UPDATE_SCRIPT = SKILL_DIR / "scripts" / "check_update.py"
REFERENCES = (
    "references/fast-path-playbook.md",
    "references/benchmark.md",
    "references/douyin-image-post-prepublish.md",
)
REQUIRED = (
    ROOT / "LICENSE",
    ROOT / "README.md",
    ROOT / "README_EN.md",
    ROOT / "CLAUDE.md",
    ROOT / "docs" / "agent-workflow.md",
    ROOT / ".github" / "workflows" / "validate.yml",
    ROOT / ".github" / "labels.json",
    SKILL_FILE,
    OPENAI_YAML,
    VERSION_FILE,
    UPDATE_SCRIPT,
    *(SKILL_DIR / reference for reference in REFERENCES),
    ROOT / "tools" / "submit_feedback.py",
    ROOT / "tests" / "test_check_update.py",
    ROOT / "tests" / "test_agent_workflow.py",
)
# 本地运行时产生、不进仓库的目录，不参与公开文本扫描。
IGNORED_DIRS = {".git", ".agent-in", ".agent-out", ".venv", "venv", "__pycache__", ".pytest_cache"}
# 维护文档里用反引号引用的仓库内路径，必须真实存在。
DOC_PATH_PREFIXES = ("skills/", "scripts/", "tools/", "tests/", "docs/", ".github/")
DOC_PATH_PATTERN = re.compile(
    r"`((?:%s)[^`\s]*)`" % "|".join(re.escape(prefix) for prefix in DOC_PATH_PREFIXES)
)
MAINTENANCE_DOCS = ("README.md", "README_EN.md", "CLAUDE.md", "docs/agent-workflow.md")


def relative(path):
    return path.relative_to(ROOT)


def check_required(errors):
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"缺少文件: {relative(path)}")


def check_skill(errors):
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

    for reference in REFERENCES:
        if reference not in skill_text:
            errors.append(f"SKILL.md 未链接参考文件: {reference}")


def check_version(errors):
    if VERSION_FILE.is_file() and VERSION_FILE.read_text(encoding="utf-8").strip() != VERSION:
        errors.append(f"VERSION 必须为 {VERSION}")


def check_openai_yaml(errors):
    yaml_text = OPENAI_YAML.read_text(encoding="utf-8") if OPENAI_YAML.is_file() else ""
    if f"${NAME}" not in yaml_text:
        errors.append("agents/openai.yaml default_prompt 未引用当前 Skill")


def public_text_files():
    for path in sorted(ROOT.rglob("*")):
        parts = path.relative_to(ROOT).parts
        if (
            path.is_file()
            and not IGNORED_DIRS.intersection(parts)
            and path.suffix in {".md", ".py", ".yaml", ".yml", ""}
        ):
            yield path


def check_public_text(errors):
    local_path_marker = "/" + "Users/"
    for path in public_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if local_path_marker in text:
            errors.append(f"包含本机绝对路径: {relative(path)}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            clean = target.split("#", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:")):
                continue
            if not (path.parent / clean).resolve().exists():
                errors.append(f"{relative(path)} 链接不存在: {target}")


def check_doc_paths(errors, docs=None):
    """docs 为 {文档名: 文本}；默认读取 MAINTENANCE_DOCS。路径都相对仓库根目录。"""
    if docs is None:
        docs = {
            name: (ROOT / name).read_text(encoding="utf-8")
            for name in MAINTENANCE_DOCS
            if (ROOT / name).is_file()
        }
    for name, text in docs.items():
        for raw in DOC_PATH_PATTERN.findall(text):
            path = raw.split("#", 1)[0].rstrip("/.,，。")
            if any(ch in path for ch in "*{<"):
                continue
            if not (ROOT / path).exists():
                errors.append(f"{name} 引用的路径不存在: {path}")


def check_python(errors):
    files = [UPDATE_SCRIPT] if UPDATE_SCRIPT.is_file() else []
    for pattern in ("scripts/*.py", "tools/*.py", "tests/*.py", ".github/scripts/*.py"):
        files += sorted(ROOT.glob(pattern))
    with tempfile.TemporaryDirectory() as tmp:
        for index, path in enumerate(files):
            try:
                py_compile.compile(str(path), cfile=str(Path(tmp) / f"{index}.pyc"), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append(f"Python 语法错误: {relative(path)}: {exc.msg.strip()}")


def check_labels(errors):
    path = ROOT / ".github" / "labels.json"
    if not path.is_file():
        return
    try:
        labels = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f".github/labels.json 不是有效 JSON: {exc}")
        return
    names = [label.get("name", "") for label in labels]
    if len(names) != len(set(names)):
        errors.append(".github/labels.json 有重名标签")
    for label in labels:
        if not label.get("name"):
            errors.append(".github/labels.json 有缺少 name 的标签")
        if not re.fullmatch(r"[0-9a-f]{6}", label.get("color", "")):
            errors.append(f"标签颜色不是 6 位十六进制: {label.get('name')}")


CHECKS = (
    check_required,
    check_skill,
    check_version,
    check_openai_yaml,
    check_public_text,
    check_doc_paths,
    check_python,
    check_labels,
)


def validate():
    errors = []
    for check in CHECKS:
        check(errors)
    return errors


def main():
    errors = validate()
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Repository is valid: {NAME} v{VERSION}")


if __name__ == "__main__":
    main()
