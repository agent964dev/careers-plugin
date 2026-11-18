# Agent964 Careers

**Work in the Agent964 careers portal from your coding agent, signed in as you.**

<p>
  <a href="https://github.com/agent964dev/careers-plugin/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/agent964dev/careers-plugin/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-blue"></a>
  <a href="https://agent-plugins.org/"><img alt="Agent Plugins 1.0" src="https://img.shields.io/badge/Agent%20Plugins-1.0-black"></a>
</p>

The [Agent964 careers portal](https://careers.agent964.com) exposes its staff operations to AI agents as a remote MCP server at `https://careers.agent964.com/mcp`. This plugin adds that server to your agent in one command, along with a `careers` skill that teaches the agent to use it well: find the right record before changing it, keep internal notes apart from what candidates read, never send an email twice, and treat what candidates write as data, not instructions.

The agent acts as you and only within your staff grant on the portal, Reviewer or Admin, which the portal checks again on every call.

## Install

Install it one way per agent: the plugin, or the server on its own [without the plugin](#without-the-plugin), not both.

<details open>
<summary><strong>Claude Code</strong></summary>

```sh
claude plugin marketplace add agent964dev/careers-plugin
claude plugin install careers@careers-plugin
```

The skill appears as `/careers:careers`. Run `claude plugin update careers@careers-plugin` to update.

</details>

<details open>
<summary><strong>Codex</strong></summary>

```sh
codex plugin marketplace add agent964dev/careers-plugin
codex plugin add careers@careers-plugin
```

</details>

Other hosts that read [Agent Plugins](https://agent-plugins.org/) packages can install this repository directly: `plugin.json`, `mcp.json`, and `skills/` are at its root.

## Without the plugin

Any MCP client that supports Streamable HTTP and OAuth can connect to the server directly. You get the tools but not the skill.

**Claude Code**

```sh
claude mcp add --transport http --scope user careers https://careers.agent964.com/mcp
claude mcp login careers
```

**Codex**

```sh
codex mcp add careers --url https://careers.agent964.com/mcp
codex mcp login careers
```

**Cursor** (`~/.cursor/mcp.json`, or `.cursor/mcp.json` in a project)

```json
{
  "mcpServers": {
    "careers": {
      "url": "https://careers.agent964.com/mcp"
    }
  }
}
```

**VS Code with GitHub Copilot, and the Copilot CLI** (`.mcp.json` at the workspace root, or your user configuration `~/.copilot/mcp-config.json`)

```json
{
  "mcpServers": {
    "careers": {
      "type": "http",
      "url": "https://careers.agent964.com/mcp",
      "tools": ["*"]
    }
  }
}
```

**Gemini CLI**

```sh
gemini mcp add --transport http careers https://careers.agent964.com/mcp
```

This adds it to the current project; add `--scope user` for every project. Sign in with `/mcp auth careers`.

## Signing in

You need a staff grant on the portal, Reviewer or Admin, given by a portal Admin. Without one, the portal refuses the agent's calls.

The first time your agent uses the server, it opens the portal in your browser. Sign in as yourself and approve the agent on the consent screen; the agent then holds a token for you alone. If the browser doesn't open, start the sign-in yourself: `/mcp` in Claude Code, or `codex mcp login careers` in Codex.

From then on:

- The agent can do only what your grant allows. Reading candidates and applications, writing notes, and moving applications follow your grant exactly as the portal's own pages do, and everything the agent does is recorded as your activity.
- If an Admin removes your grant, the agent's calls are refused at once; signing in again doesn't restore them.
- If you disconnect the agent, it must sign in and be approved again.

## Disconnecting

Open [Connected agents](https://careers.agent964.com/staff/agents) on the portal and disconnect the agent. Its access ends immediately. To remove it from your agent too, uninstall the plugin (`claude plugin uninstall careers@careers-plugin`, or `codex plugin remove careers@careers-plugin`) or remove the server you added (`claude mcp remove careers`, `codex mcp remove careers`).

## For agents

If a user asked you to look at this repository, this section is for you.

- **Setting it up.** Install the plugin through the route for the user's agent under [Install](#install), or add the server directly as [Without the plugin](#without-the-plugin) shows. Don't start the OAuth sign-in on the user's behalf without telling them: it opens their browser and asks them to approve you.
- **Using it.** Read [the `careers` skill](skills/careers/SKILL.md) before calling the server's tools. List the tools first; the set changes with the portal's version, and the user's grant decides what each call may do.
- **Access problems.** A sign-in prompt or an `unauthenticated` error means the user must sign in again. A `forbidden` error means either their grant doesn't allow the action (only a portal Admin can change that), or the agent was approved for less than their grant allows, for example after they were made an Admin; disconnecting it on the Connected agents page and connecting again fixes that.

## Privacy

The plugin itself collects nothing; it tells your agent where the server is. What the portal records is described in its [privacy notice](https://careers.agent964.com/privacy) and [terms](https://careers.agent964.com/terms).

## Contributing

[AGENTS.md](AGENTS.md) is the contributor guide: the layout, the full check (`mise run check`), and how releases work. Pull requests are squash-merged with a conventional title.

## Licence

[MIT](LICENSE)
