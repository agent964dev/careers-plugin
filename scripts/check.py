# /// script
# requires-python = ">=3.14"
# dependencies = ["pyyaml==6.0.3", "jsonschema==4.26.0"]
# ///
"""Check the plugin: skill metadata, links, plugin manifests against their schemas, the MCP declarations,
and the version every manifest shares.

Usage: mise run check (or uv run scripts/check.py)
"""

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
SCHEMAS = ROOT / "scripts" / "schemas"
PORTABLE_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PORTABLE_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
# The one server this plugin declares, in each host's dialect: the portable format names the transport
# streamable-http, Claude Code's .mcp.json names it http.
SERVER = "careers"
SERVER_URL = "https://careers.agent964.com/mcp"
MARKETPLACE = "careers-plugin"
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(\s*)(```|~~~)")

problems = []


def problem(path, message):
    problems.append(f"{path.relative_to(ROOT)}: {message}")


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    return yaml.safe_load(text[4:end]) if end != -1 else None


def check_skill(skill):
    entry = skill / "SKILL.md"
    if not entry.is_file():
        problem(skill, "missing SKILL.md")
        return
    meta = frontmatter(entry)
    if not isinstance(meta, dict):
        problem(entry, "frontmatter missing or not a mapping")
        return
    if meta.get("name") != skill.name or not NAME.match(skill.name) or len(skill.name) > 64:
        problem(entry, f"name must be '{skill.name}', lowercase and hyphenated, at most 64 characters")
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        problem(entry, "description must be a nonempty string of at most 1024 characters")
    agent = skill / "agents" / "openai.yaml"
    if not agent.is_file():
        problem(skill, "missing agents/openai.yaml")
    else:
        interface = (yaml.safe_load(agent.read_text()) or {}).get("interface", {})
        for field in ("display_name", "short_description", "default_prompt"):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                problem(agent, f"interface.{field} must be a nonempty string")
    for nested in skill.rglob("SKILL.md"):
        if nested != entry:
            problem(nested, "a nested SKILL.md is discovered as a separate skill; rename it")
    for path in skill.rglob("*"):
        if path.is_symlink():
            problem(path, "plugin directories reject symlinked components")


def check_links(path):
    fence = None
    for number, line in enumerate(path.read_text().splitlines(), 1):
        opened = FENCE.match(line)
        if opened:
            fence = None if fence == opened.group(2) else fence or opened.group(2)
            continue
        if fence:
            continue
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if not resolved.exists():
                problem(path, f"line {number}: link target '{target}' does not exist")


def load(relative):
    path = ROOT / relative
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        problem(path, f"unreadable JSON: {error}")
        return {}


def validate(relative, document, schema_file):
    """Validate against a vendored copy of the schema; scripts/schemas/README.md names each source."""
    schema = json.loads((SCHEMAS / schema_file).read_text())
    validator = jsonschema.validators.validator_for(schema)(schema)
    for error in sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path)):
        location = "/".join(str(part) for part in error.absolute_path) or "(root)"
        problem(ROOT / relative, f"{location}: {error.message} [{schema_file}]")


def check_manifests():
    portable = load("plugin.json")
    claude = load(".claude-plugin/plugin.json")
    marketplace = load(".claude-plugin/marketplace.json")
    release = load(".release-please-manifest.json")
    validate("plugin.json", portable, "agent-plugins-plugin.schema.json")
    validate(".claude-plugin/plugin.json", claude, "claude-code-plugin-manifest.schema.json")
    validate(".claude-plugin/marketplace.json", marketplace, "claude-code-marketplace.schema.json")
    if portable.get("$schema") != PORTABLE_SCHEMA:
        problem(ROOT / "plugin.json", f"$schema must be {PORTABLE_SCHEMA}")
    name = portable.get("name")
    if not isinstance(name, str) or not NAME.match(name):
        problem(ROOT / "plugin.json", "name must be lowercase and hyphenated")
    if marketplace.get("name") != MARKETPLACE:
        problem(ROOT / ".claude-plugin/marketplace.json", f"marketplace name must be '{MARKETPLACE}', which the install commands use")
    entries = marketplace.get("plugins") or [{}]
    if len(entries) != 1 or entries[0].get("source") != "./":
        problem(ROOT / ".claude-plugin/marketplace.json", "the marketplace lists exactly this plugin, with source './'")
    version = portable.get("version")
    if not isinstance(version, str) or not SEMVER.match(version):
        problem(ROOT / "plugin.json", "version must be MAJOR.MINOR.PATCH")
    for label, value in (
        ("Claude manifest name", claude.get("name")),
        ("marketplace plugin name", entries[0].get("name")),
    ):
        if value != name:
            problem(ROOT / ".claude-plugin", f"{label} '{value}' differs from plugin.json '{name}'")
    for label, value in (
        ("Claude manifest version", claude.get("version")),
        ("release-please version", release.get(".")),
        ("version.txt", (ROOT / "version.txt").read_text().strip() if (ROOT / "version.txt").exists() else None),
    ):
        if value != version:
            problem(ROOT, f"{label} '{value}' differs from plugin.json version '{version}'")
    for field in ("description", "author", "homepage", "repository", "license", "keywords"):
        if claude.get(field) != portable.get(field):
            problem(ROOT / ".claude-plugin/plugin.json", f"{field} differs from plugin.json")


def check_mcp():
    portable = load("mcp.json")
    claude = load(".mcp.json")
    validate("mcp.json", portable, "agent-plugins-mcp.schema.json")
    if portable.get("$schema") != PORTABLE_MCP_SCHEMA:
        problem(ROOT / "mcp.json", f"$schema must be {PORTABLE_MCP_SCHEMA}")
    expected = {
        "mcp.json": (portable, {SERVER: {"type": "streamable-http", "url": SERVER_URL}}),
        ".mcp.json": (claude, {SERVER: {"type": "http", "url": SERVER_URL}}),
    }
    for relative, (document, servers) in expected.items():
        if document.get("mcpServers") != servers:
            problem(ROOT / relative, f"mcpServers must be exactly {json.dumps(servers)}")
    if set(claude) - {"mcpServers"}:
        problem(ROOT / ".mcp.json", "only mcpServers belongs at the top level")


def main():
    skills = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    for skill in skills:
        check_skill(skill)
    for path in sorted([*SKILLS.rglob("*.md"), *ROOT.glob("*.md")]):
        check_links(path)
    check_manifests()
    check_mcp()

    for line in problems:
        print(line)
    print(f"{len(skills)} skills checked; {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
