# Flight Buddy MCP Server

MCP server that exposes flight tools backed by **SerpApi Google Flights**.

## Tools

| Tool | Purpose |
|------|---------|
| `search_flights` | Live search (IATA codes + dates) |
| `rank_flights` | Rank by cheapest / fastest / fewest_stops / balanced |
| `get_flight_details` | Summarize one offer |

## Resources / prompts

- Resource: `baggage://policy`
- Prompt: `find_best_flight`

## Run standalone (stdio)

```bash
cd mcp-servers/flight-buddy
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SERPAPI_API_KEY=your_key
python server.py
```

The Samiaa **web backend** starts this process automatically as an MCP client host.
