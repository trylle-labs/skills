#!/usr/bin/env python3

import json
import re
import struct
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


def png_size(path: Path):
    header = path.read_bytes()[:24]
    require(header[:8] == b"\x89PNG\r\n\x1a\n", f"{path.relative_to(ROOT)} is not a PNG")
    return struct.unpack(">II", header[16:24])


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
    require(versions == {"0.1.4"}, f"plugin versions disagree: {sorted(versions)}")
    description = "Create and manage repositories, pull requests and reviews, issues, stacked changes, CI workflows, automations, secrets and variables, organization settings, SSH keys, and developer utilities on Trylle."
    require(codex["description"] == description, "invalid Codex description")
    require(cursor["description"] == description, "invalid Cursor description")
    require(claude["description"] == description, "invalid Claude description")
    require(codex["interface"].get("shortDescription") == "Repositories, PRs, issues, CI, and automations", "invalid Codex short description")
    require(codex["interface"].get("longDescription") == description, "invalid Codex long description")
    marketplace_description = "Trylle workflows for repositories, pull requests, issues, CI, and automations."
    require(cursor_market["metadata"]["description"] == marketplace_description, "invalid Cursor marketplace summary")
    require(claude_market["description"] == marketplace_description, "invalid Claude marketplace summary")
    require(cursor_market["plugins"][0]["description"] == description, "invalid Cursor marketplace description")
    require(claude_market["plugins"][0]["description"] == description, "invalid Claude marketplace description")
    require(codex.get("skills") == "./skills/", "Codex must load ./skills/")
    require(cursor.get("skills") == "./skills/", "Cursor must load ./skills/")
    require(codex["interface"].get("composerIcon") == "./assets/trylle-32.png", "invalid Codex composer icon")
    require(codex["interface"].get("logo") == "./assets/trylle-512.png", "invalid Codex logo")
    require(cursor.get("logo") == "assets/trylle-512.png", "invalid Cursor logo")
    logo = PLUGIN / "assets" / "trylle-512.png"
    composer_icon = PLUGIN / "assets" / "trylle-32.png"
    require(logo.is_file(), "plugin logo asset is missing")
    require(composer_icon.is_file(), "plugin composer icon asset is missing")
    require(png_size(logo) == (512, 512), "plugin logo must be 512x512")
    require(png_size(composer_icon) == (32, 32), "plugin composer icon must be 32x32")
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
