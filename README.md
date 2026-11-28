# skills

Reviewed agent skill packs from the
[Packy Catalog](https://github.com/yersonargotev/packy-catalog), packaged for
[APM](https://github.com/microsoft/apm).

Each directory under `packs/` is a self-contained APM package: skills in
`skills/<name>/SKILL.md`, plus agents and instructions under `.apm/` where the
Pack has them. Upstream license notices are preserved in each package's
`notices/` directory, and `apm.yml` records the pinned upstream commits.

## Install

```sh
brew install apm

# A whole pack
apm install yersonargotev/skills/packs/matty

# Selected skills from a pack
apm install yersonargotev/skills/packs/matty --skill tdd --skill code-review

# A single skill
apm install yersonargotev/skills/packs/emil/skills/animate

# Through the marketplace
apm marketplace add yersonargotev/skills
apm install matty@skills
```

Append `#<tag-or-commit>` to pin a version. APM deploys to the targets declared
in your project's `apm.yml` (`claude`, `codex`, `copilot`, `cursor`, ...).

Some Packs carry skills written differently for Claude Code. Those ship as a
second `<pack>-claude` package; install it instead of the base package in
Claude Code projects, or scope each one with `targets:` in your `apm.yml`.

## Packages

<!-- packages:start -->
| Package | Version | Skills | Description |
| --- | --- | --- | --- |
| [`addy`](packs/addy) | 5.1.0 | 36 | Addy agent skills |
| [`argote`](packs/argote) | 5.2.0 | 4 | Yerson Argote's engineering, communication, and issue-delivery workflows |
| [`claude`](packs/claude) | 2.0.0 | 2 | Portable HTML explanation and planning skills from the Claude community repository |
| [`cursor-team-kit`](packs/cursor-team-kit) | 1.0.0 | 3 | Cursor Team Kit skills for removing code slop and driving local CLI and UI harnesses |
| [`emil`](packs/emil) | 4.0.0 | 20 | Emil Kowalski skills for UI design, web and Expo animation, mobile polish, Swift, and frontend libraries |
| [`humanlayer`](packs/humanlayer) | 4.0.0 | 6 | HumanLayer skills for visual explanations, pull requests, React types, and agentic workflows |
| [`matty`](packs/matty) | 5.0.2 | 35 | Matty workflow |
| [`orchestrate`](packs/orchestrate) | 4.0.0 | 1 | Coordinate focused Codex subagents |
| [`packy`](packs/packy) | 1.2.0 | 1 | Discover and obtain reviewed Catalog skills through the Packy CLI (Agents variants; use the -claude package for Claude Code) |
| [`packy-claude`](packs/packy-claude) | 1.2.0 | 1 | Discover and obtain reviewed Catalog skills through the Packy CLI (Claude Code variants) |
| [`ponytail`](packs/ponytail) | 3.0.1 | 6 | Ponytail 5 minimal-code guidance and six skills, adapted for Packy without plugin runtime hooks |
| [`pstack`](packs/pstack) | 6.3.0 | 59 | Apply pstack's reviewed portable engineering workflows and principles (Agents variants; use the -claude package for Claude Code) |
| [`pstack-claude`](packs/pstack-claude) | 6.3.0 | 59 | Apply pstack's reviewed portable engineering workflows and principles (Claude Code variants) |
| [`thermos`](packs/thermos) | 3.0.0 | 3 | Thermos correctness, security, and maintainability reviews with portable reviewer agents |
| [`warp`](packs/warp) | 2.6.0 | 29 | Warp common engineering and agent workflows |
| [`web`](packs/web) | 4.0.1 | 3 | Web automation and React engineering skills |
<!-- packages:end -->

## Maintain

`packs/`, the root `apm.yml`, and the table above are generated from a Packy
Catalog checkout. Do not edit them by hand:

```sh
scripts/sync_catalog.py ../packy-catalog
apm pack   # refreshes .claude-plugin/marketplace.json
```
