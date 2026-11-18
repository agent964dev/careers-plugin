# Agent964 Careers plugin

A plugin that connects coding agents to the Agent964 careers portal's staff MCP server (`https://careers.agent964.com/mcp`) and teaches them to use it. It declares the server once per host dialect and ships one skill:

- `plugin.json` and `mcp.json` are the portable [Agent Plugins](https://agent-plugins.org/) manifest and MCP configuration, which Codex and other Agent Plugins hosts read. The portable manifest is closed, so the server lives only in `mcp.json`, with transport `streamable-http`.
- `.claude-plugin/plugin.json` and `.mcp.json` are Claude Code's manifest and MCP configuration, with transport `http`. `.claude-plugin/marketplace.json` is the marketplace `careers-plugin` that both Claude Code and Codex add from this repository.
- `skills/careers/` is the skill: a `SKILL.md` and an `agents/openai.yaml` for Codex's interface.

The server's name (`careers`) and URL are the same in both MCP files. The portal handles sign-in, consent, and grants through OAuth discovery, so no file here carries credentials, headers, or client registration.

## Working on the skill

Write or revise it with the `skill-writing` skill. It must stay true for any version of the portal: describe workflows and the portal's rules, and never name a tool the server might not offer, since the tools are generated from the portal's staff operations and change with its versions (every staff tool is listed; the person's grant decides what a call may do). Examples use synthetic people such as `ada.synthetic@example.test`, never real candidates.

A file named `SKILL.md` anywhere below a skill's folder is installed as a separate skill, so templates use another name.

## Checks

Tools are pinned in `mise.toml`; run `mise install` once. `mise run check` is the full check, and CI runs exactly that. It validates the skill's metadata, links, and Codex interface; each manifest and `mcp.json` against its schema (vendored in `scripts/schemas/`, whose README names each source); the server declared identically in both MCP files; and the version every manifest shares. Before a release that changes a manifest, also run `claude plugin validate .`, Claude Code's authoritative check.

## Releases

Pull requests are squash-merged with a conventional title, such as `feat(skill): explain stage moves` or `fix: correct the server URL`. release-please turns those titles into a release pull request that bumps `version.txt`, both plugin manifests, and `CHANGELOG.md`; merging it publishes the release. Claude Code updates an installed plugin only when its version changes. A release pull request runs CI only when the repository has a `RELEASE_PLEASE_TOKEN` secret (GitHub starts no workflow from the default token); without it, run the check from the Actions tab before merging.
