#!/usr/bin/env python3

import json
import re
import struct
import sys
from pathlib import Path

try:
    import yaml
except ImportError as error:
    raise SystemExit(
        "validation error: PyYAML is required; install it with "
        "`python3 -m pip install PyYAML`"
    ) from error


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "trylle"
SKILLS = PLUGIN / "skills"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
LOCAL_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_PATTERN = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", re.DOTALL)
SPEC_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}


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


def parse_agent_skills_frontmatter(path: Path):
    text = path.read_text()
    match = FRONTMATTER_PATTERN.match(text)
    require(match is not None, f"{path.relative_to(ROOT)} has invalid frontmatter")

    try:
        fields = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise AssertionError(f"{path.relative_to(ROOT)} has invalid YAML frontmatter: {error}") from error

    require(isinstance(fields, dict), f"{path.relative_to(ROOT)} frontmatter must be a YAML mapping")
    require(
        all(isinstance(key, str) for key in fields),
        f"{path.relative_to(ROOT)} frontmatter field names must be strings",
    )
    unsupported = sorted(set(fields) - SPEC_FRONTMATTER_FIELDS)
    require(
        not unsupported,
        f"{path.relative_to(ROOT)} has unsupported Agent Skills frontmatter field(s): {', '.join(unsupported)}",
    )
    missing = sorted({"name", "description"} - set(fields))
    require(
        not missing,
        f"{path.relative_to(ROOT)} is missing required frontmatter field(s): {', '.join(missing)}",
    )

    return text, fields, match.group(2)


def validate_agent_skill(skill: Path):
    skill_file = skill / "SKILL.md"
    require(skill_file.is_file(), f"{skill.relative_to(ROOT)} is missing SKILL.md")
    text, fields, body = parse_agent_skills_frontmatter(skill_file)

    name = fields["name"]
    description = fields["description"]
    require(isinstance(name, str), f"{skill_file.relative_to(ROOT)} name must be a string")
    require(isinstance(description, str), f"{skill_file.relative_to(ROOT)} description must be a string")
    require(1 <= len(name) <= 64, f"{skill_file.relative_to(ROOT)} name must be 1-64 characters")
    require(SKILL_NAME_PATTERN.fullmatch(name) is not None, f"{skill_file.relative_to(ROOT)} has an invalid skill name")
    require(name == skill.name, f"{skill_file.relative_to(ROOT)} name must match its parent directory")
    require(1 <= len(description) <= 1024, f"{skill_file.relative_to(ROOT)} description must be 1-1024 characters")
    if "license" in fields:
        license_value = fields["license"]
        require(
            isinstance(license_value, str) and license_value.strip(),
            f"{skill_file.relative_to(ROOT)} license must be a non-empty string",
        )
    if "compatibility" in fields:
        compatibility = fields["compatibility"]
        require(
            isinstance(compatibility, str) and 1 <= len(compatibility) <= 500,
            f"{skill_file.relative_to(ROOT)} compatibility must be a 1-500 character string",
        )
    if "metadata" in fields:
        metadata = fields["metadata"]
        require(isinstance(metadata, dict), f"{skill_file.relative_to(ROOT)} metadata must be a mapping")
        require(
            all(isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()),
            f"{skill_file.relative_to(ROOT)} metadata keys and values must be strings",
        )
    if "allowed-tools" in fields:
        allowed_tools = fields["allowed-tools"]
        require(
            isinstance(allowed_tools, str) and allowed_tools.strip(),
            f"{skill_file.relative_to(ROOT)} allowed-tools must be a non-empty space-separated string",
        )
    require(body.strip(), f"{skill_file.relative_to(ROOT)} must contain Markdown instructions")
    require(len(text.splitlines()) <= 500, f"{skill_file.relative_to(ROOT)} should stay under 500 lines")

    for link in LOCAL_LINK_PATTERN.findall(body):
        target = link.split("#", 1)[0]
        if not target or "://" in target or target.startswith(("#", "mailto:")):
            continue
        require(not Path(target).is_absolute(), f"{skill_file.relative_to(ROOT)} uses an absolute file reference: {link}")
        require(".." not in Path(target).parts, f"{skill_file.relative_to(ROOT)} file references must stay inside the skill: {link}")
        require((skill / target).is_file(), f"{skill_file.relative_to(ROOT)} references missing file: {link}")


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
    require(len(versions) == 1, f"plugin versions disagree: {sorted(versions)}")
    version = versions.pop()
    require(SEMVER_PATTERN.fullmatch(version) is not None, f"invalid plugin version: {version}")
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
    require(claude.get("skills") == "./skills/", "Claude must load ./skills/")
    require(codex["interface"].get("composerIcon") == "./assets/trylle-48.png", "invalid Codex composer icon")
    require(codex["interface"].get("logo") == "./assets/trylle-512.png", "invalid Codex logo")
    require(cursor.get("logo") == "assets/trylle-512.png", "invalid Cursor logo")
    logo = PLUGIN / "assets" / "trylle-512.png"
    composer_icon = PLUGIN / "assets" / "trylle-48.png"
    require(logo.is_file(), "plugin logo asset is missing")
    require(composer_icon.is_file(), "plugin composer icon asset is missing")
    require(png_size(logo) == (512, 512), "plugin logo must be 512x512")
    require(png_size(composer_icon) == (48, 48), "plugin composer icon must be 48x48")
    require(codex_market["plugins"][0]["source"]["path"] == "./plugins/trylle", "invalid Codex source")
    require(cursor_market["plugins"][0]["source"] == "plugins/trylle", "invalid Cursor source")
    require(claude_market["plugins"][0]["source"] == "./plugins/trylle", "invalid Claude source")
    require(cursor_market["metadata"]["version"] == version, "Cursor marketplace version must match the plugin")

    skill_dirs = sorted(path.parent for path in SKILLS.glob("*/SKILL.md"))
    require(skill_dirs, "plugin must contain at least one Agent Skill")
    for skill_dir in skill_dirs:
        validate_agent_skill(skill_dir)
        skill_name = skill_dir.name
        openai_yaml = (skill_dir / "agents" / "openai.yaml").read_text()
        require(f"${skill_name}" in openai_yaml, f"{skill_name} default prompt must mention ${skill_name}")

    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts:
            require(placeholder not in path.read_text(errors="ignore"), f"{path.relative_to(ROOT)} contains a placeholder")

    print(f"Validated {len(skill_dirs)} Agent Skill and Codex, Cursor, and Claude Code plugin metadata at version {version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"validation error: {error}", file=sys.stderr)
        raise SystemExit(1)
