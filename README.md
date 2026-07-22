# Trylle Skills

Official Agent Skills and plugins for using the [`try`](https://trylle.com/trylle/trylle-cli) CLI with Trylle.

The repository keeps the operational workflow in one [Agent Skills](https://agentskills.io/specification)-compatible folder and exposes that same folder through harness-specific manifests for Codex, Cursor, and Claude Code.

## Included

- `trylle-cli`: manage repositories, pull requests, issues, stacks, CI, actions configuration, organizations, automations, and other Trylle resources with `try`.
- Codex plugin and marketplace metadata.
- Cursor plugin and multi-plugin marketplace metadata.
- Claude Code plugin and marketplace metadata.

The canonical portable skill is [`skills/trylle-cli`](./skills/trylle-cli/). Its `SKILL.md`, references, and optional Codex UI metadata stay together so the directory can be copied or linked into a skills directory without the plugin wrapper.

## Install the Trylle CLI

```bash
npm i -g @trylle/trylle-cli

try auth status
```

If authentication is not configured, create an API key in Trylle and save it without placing the key directly in shell history:

```bash
try auth login
```

## Default Installation via Skills.sh

```
npx skills add trylle-labs/skills
```

Alternative route using Astral `uv`:

```
uvx upd-skill -g trylle-labs/trylle-cli
```

## Install the Agent Skill directly

Use the direct skill install when you only need the workflow and already have the `try` CLI. Codex and Cursor both discover user skills under `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills
cp -R skills/trylle-cli ~/.agents/skills/
```

Claude Code discovers user skills under `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
cp -R skills/trylle-cli ~/.claude/skills/
```

For a repository-scoped install, use `.agents/skills/` for Codex and Cursor or `.claude/skills/` for Claude Code. Copy the complete `trylle-cli` directory; `SKILL.md` references files relative to that directory.

## Install the plugin

This repository is the marketplace root for Codex and Claude Code. The installable plugin root is [`plugins/trylle`](./plugins/trylle/), and each marketplace manifest points at that folder.

### Codex

Add the Git-backed marketplace:

```bash
codex plugin marketplace add https://trylle.com/trylle/skills.git
```

Then install `trylle` from the `Trylle` marketplace:

```bash
codex plugin add trylle@trylle
```

In the ChatGPT desktop app, you can also open **Plugins**, choose the **Trylle** marketplace, and install **trylle** from there. Start a new Codex task after installation so the bundled skill is available in the task context.

### Cursor

Cursor supports local plugin loading from `~/.cursor/plugins/local/<plugin-name>/`. For a Trylle-hosted checkout, clone the repository and symlink the plugin root into Cursor's local plugin directory:

```bash
try repo clone trylle/skills trylle-skills
mkdir -p ~/.cursor/plugins/local
ln -s "$PWD/trylle-skills/plugins/trylle" ~/.cursor/plugins/local/trylle
```

Restart Cursor or run **Developer: Reload Window**. The plugin root must be `plugins/trylle`, not the repository root.

### Claude Code

Claude Code installs plugins from marketplaces. Add this repository as a marketplace, then install the `trylle` plugin from the `trylle` marketplace:

```bash
claude plugin marketplace add https://trylle.com/trylle/skills.git
claude plugin install trylle@trylle
```

Inside an existing Claude Code session, reload plugins before invoking the skill:

```text
/reload-plugins
/trylle:trylle-cli
```

For local testing from a checkout, add the checkout directory instead of the Git URL:

```bash
claude plugin marketplace add /path/to/skills
claude plugin install trylle@trylle
```

## Repository layout

```text
├── .agents
│   └── plugins
│       └── marketplace.json          # Codex et al marketplace
├── .claude-plugin
│   └── marketplace.json              # Claude Code marketplace
├── .cursor-plugin
│   └── marketplace.json              # Cursor marketplace
├── LICENSE
├── README.md
├── plugins
│   └── trylle
│       ├── .claude-plugin
│       │   └── plugin.json
│       ├── .codex-plugin
│       │   └── plugin.json
│       ├── .cursor-plugin
│       │   └── plugin.json
│       ├── assets
│       │   ├── trylle-48.png         # Codex composer icon
│       │   └── trylle-512.png        # Codex and Cursor plugin logo
│       └── skills -> ../../skills    # Symink to the actual skill source
├── scripts
│   └── validate.py
└── skills
    └── trylle-cli
        ├── SKILL.md                  # trylle-cli skill source
        ├── agents
        │   └── openai.yaml
        └── references
            ├── command-catalog.md    # trylle-cli commands mapping
            └── workflows.md          # trylle-cli example workflows
```

All three plugin manifests explicitly load the same `plugins/trylle/skills/` directory. Keep shared behavior in the Agent Skill rather than copying harness-specific instructions.

## Validate changes

```bash
python3 scripts/validate.py
```

The repository validator checks the portable Agent Skills constraints and the Codex, Cursor, and Claude Code plugin wiring. When the official reference CLI is installed, validate the canonical skill with it too:

```bash
skills-ref validate skills/trylle-cli
```

When the relevant harness is installed, also run its native validator or local loading flow.
