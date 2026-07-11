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
brew install trylle/trylle-cli/try
try auth status --json
```

If authentication is not configured, create an API key in Trylle and save it without placing the key directly in shell history:

```bash
export TRYLLE_API_KEY="..."
try auth login --json
unset TRYLLE_API_KEY
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

### Codex

Add the Git-backed marketplace:

```bash
codex plugin marketplace add https://api.trylle.com/git/trylle/skills.git
```

Then open the plugin directory in the ChatGPT desktop app and install `trylle` from the `Trylle` marketplace.

### Cursor

Cursor currently documents local plugin loading and GitHub-backed marketplace submission. For a Trylle-hosted checkout, clone the repository and symlink the plugin into Cursor's local plugin directory:

```bash
try repo clone trylle/skills trylle-skills
mkdir -p ~/.cursor/plugins/local
ln -s "$PWD/trylle-skills/plugins/trylle" ~/.cursor/plugins/local/trylle
```

Restart Cursor or run **Developer: Reload Window**.

### Claude Code

Claude Code accepts full Git URLs for marketplaces hosted outside GitHub:

```bash
claude plugin marketplace add https://api.trylle.com/git/trylle/skills.git
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
│       │   ├── trylle-32.png         # Codex composer icon
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
