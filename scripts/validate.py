#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "trylle"
SKILL = PLUGIN / "skills" / "use-trylle"


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise AssertionError(f"{path.relative_to(ROOT)}: {error}") from error


def require(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def main() -> int:
    placeholder = "[" + "TO" + "DO:"
    codex = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    cursor = load_json(PLUGIN / ".cursor-plugin" / "plugin.json")
    claude = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    cursor_market = load_json(ROOT / ".cursor-plugin" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")

    names = {codex["name"], cursor["name"], claude["name"]}
    require(names == {"trylle"}, f"plugin names disagree: {sorted(names)}")
    versions = {codex["version"], cursor["version"], claude["version"]}
    require(versions == {"0.1.0"}, f"plugin versions disagree: {sorted(versions)}")
    require(codex.get("skills") == "./skills/", "Codex must load ./skills/")
    require(cursor.get("skills") == "./skills/", "Cursor must load ./skills/")
    require(codex_market["plugins"][0]["source"]["path"] == "./plugins/trylle", "invalid Codex source")
    require(cursor_market["plugins"][0]["source"] == "plugins/trylle", "invalid Cursor source")
    require(claude_market["plugins"][0]["source"] == "./plugins/trylle", "invalid Claude source")

    skill_text = (SKILL / "SKILL.md").read_text()
    require(placeholder not in skill_text, "SKILL.md contains a placeholder")
    match = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    require(match is not None, "SKILL.md has invalid frontmatter")
    fields = [line.split(":", 1)[0] for line in match.group(1).splitlines() if ":" in line]
    require(fields == ["name", "description"], f"unexpected skill frontmatter fields: {fields}")
    require("name: use-trylle" in match.group(1), "skill name does not match its directory")

    openai_yaml = (SKILL / "agents" / "openai.yaml").read_text()
    require("$use-trylle" in openai_yaml, "default prompt must mention $use-trylle")

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            require(placeholder not in path.read_text(errors="ignore"), f"{path.relative_to(ROOT)} contains a placeholder")

    print("Validated Trylle skill and Codex, Cursor, and Claude Code plugin metadata.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"validation error: {error}", file=sys.stderr)
        raise SystemExit(1)
