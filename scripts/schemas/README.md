# Vendored schemas

`scripts/check.py` validates the manifests against these copies, so the check runs offline and a change upstream reaches it only through a reviewed update. Each was fetched on 18 November 2026; refresh one by fetching its source again and committing the result.

| File | Source | Validates |
|---|---|---|
| `agent-plugins-plugin.schema.json` | https://agent-plugins.org/schemas/1.0.0/plugin.schema.json | `plugin.json` |
| `agent-plugins-mcp.schema.json` | https://agent-plugins.org/schemas/1.0.0/mcp.schema.json | `mcp.json` |
| `claude-code-plugin-manifest.schema.json` | https://json.schemastore.org/claude-code-plugin-manifest.json (SchemaStore, Apache-2.0) | `.claude-plugin/plugin.json` |
| `claude-code-marketplace.schema.json` | https://json.schemastore.org/claude-code-marketplace.json (SchemaStore, Apache-2.0) | `.claude-plugin/marketplace.json` |

Claude Code publishes no schema of its own; `claude plugin validate` is its authoritative check, and SchemaStore's community schemas are the closest machine-readable copy. They allow fields they don't list, such as `displayName`.
