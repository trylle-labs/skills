# Trylle Skills

Official Agent Skills and plugins for using the [`try`](https://trylle.com/trylle/trylle-cli) CLI with Trylle.

The repository keeps the operational workflow in one Agent Skill and exposes it through harness-specific manifests for Codex, Cursor, and Claude Code.

## Included

- `use-trylle`: manage repositories, pull requests, issues, stacks, CI, actions configuration, organizations, automations, and other Trylle resources with `try`.
- Codex plugin and marketplace metadata.
- Cursor plugin and multi-plugin marketplace metadata.
- Claude Code plugin and marketplace metadata.

## Install the Trylle CLI

```bash
brew install trylle/trylle-cli/try
try auth status --json
```

If authentication is not configured, create an API key in Trylle and save it without placing the key directly in shell history:

```bash
export TRYLLE_API_KEY="..."
try auth login --json
unset TRYLLE_API_KEY
```

## Install the plugin

### Codex

Add the Git-backed marketplace:

```bash
codex plugin marketplace add https://api.trylle.com/git/trylle/trylle-skills.git
```

Then open the plugin directory in the ChatGPT desktop app and install `trylle` from the `Trylle` marketplace.

### Cursor

Cursor currently documents local plugin loading and GitHub-backed marketplace submission. For a Trylle-hosted checkout, clone the repository and symlink the plugin into Cursor's local plugin directory:

```bash
try repo clone trylle/trylle-skills
mkdir -p ~/.cursor/plugins/local
ln -s "$PWD/trylle-skills/plugins/trylle" ~/.cursor/plugins/local/trylle
```

Restart Cursor or run **Developer: Reload Window**.

### Claude Code

Claude Code accepts full Git URLs for marketplaces hosted outside GitHub:

```bash
claude plugin marketplace add https://api.trylle.com/git/trylle/trylle-skills.git
claude plugin install trylle@trylle
```

## Repository layout

```text
.agents/plugins/marketplace.json        # Codex marketplace
.cursor-plugin/marketplace.json         # Cursor marketplace
.claude-plugin/marketplace.json         # Claude Code marketplace
plugins/trylle/
├── assets/trylle.png
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── .claude-plugin/plugin.json
└── skills/use-trylle/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
```

All three plugin manifests load the same `plugins/trylle/skills/` directory. Keep shared behavior in the Agent Skill rather than copying harness-specific instructions.

## Validate changes

```bash
python3 scripts/validate.py
```

When the relevant harness is installed, also run its native validator or local loading flow.
