# Flight Buddy MCP — Azure Function App

Remote MCP server hosted on Azure Functions (Flex Consumption).

## Tools

- `search_flights`
- `rank_flights`
- `get_flight_details`

## MCP endpoint (after deploy)

```text
https://mcp-agent123-grefe7fqabbvhjfd.eastus2-01.azurewebsites.net/runtime/webhooks/mcp
```

Authenticate with Function key header:

```http
x-functions-key: <mcp_extension system key>
```

Get the key in Azure Portal → Function App → **App keys** → `mcp_extension` (or system keys).

## Required app setting

In Azure Portal → Configuration → Application settings:

```text
SERPAPI_API_KEY=<your serpapi key>
```

## Local run

```bash
cd function-app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# set SERPAPI_API_KEY in local.settings.json
func start
```
