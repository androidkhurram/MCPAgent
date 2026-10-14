# Samiaa Learning Agents

Includes:
- **Flight Buddy (MCP)** — web host + MCP server + SerpApi Google Flights
- **Hotel Finder** — Foundry agent + Serper.dev
- **RAG Chunking Lab** — teaching UI

## Stack

- **Frontend:** React + Vite + TypeScript (`frontend/`)
- **Backend:** FastAPI + Azure AI Foundry (`backend/`)
- **MCP server:** `mcp-servers/flight-buddy/` (stdio tools)
- **Live data:** SerpApi (flights), Serper.dev (hotels)

## Prerequisites

- Python 3.11+
- Node.js 20+
- An Azure AI Foundry (or Azure OpenAI) chat deployment with tool calling
- A [Serper.dev](https://serper.dev) API key

## Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

```env
AZURE_AI_FOUNDRY_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=...
AZURE_AI_FOUNDRY_DEPLOYMENT=your-deployment-name
AZURE_API_VERSION=2024-08-01-preview
SERPER_API_KEY=...
SERPAPI_API_KEY=...
```

Run the API (from `backend/`):

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### Flight Buddy (MCP)

1. Add `SERPAPI_API_KEY` to `backend/.env`
2. Start backend + frontend
3. Open the **Flight Buddy (MCP)** tab
4. Try: `Best flight ISB to JED on 2026-10-17 under $700, fewest stops`

Architecture: **React UI → FastAPI (Host + MCP Client) → flight-buddy MCP server → SerpApi**

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The Vite dev server proxies `/api` to the backend.

## Example query

> I want to travel to Dubai Mar 10–15, king room near Burj Khalifa, under $250/night. Find the best hotels.

The agent extracts requirements, calls `search_hotels` (Serper), ranks options, and returns chat text plus hotel cards with source links.

## API

### `POST /api/chat`

```json
{
  "messages": [
    { "role": "user", "content": "Dubai Mar 10-15, king room under $250 near Downtown" }
  ]
}
```

Response:

```json
{
  "message": "Here are the best matches…",
  "hotels": [
    {
      "name": "Example Hotel",
      "price_hint": "$199/night",
      "why": "Near Downtown and within budget",
      "link": "https://…",
      "snippet": "…"
    }
  ],
  "status": "Searching live rates…"
}
```

## Limitations

- Serper/Google snippets are **approximate**, not booking-grade inventory.
- Prices and availability can change; always verify on the source link.
- The agent is instructed not to invent hotels/prices; quality still depends on search results.
- Single agent only in v1 (no flights, maps, or booking checkout).

## Project layout

```
backend/
  app/main.py
  app/config.py
  app/agent/orchestrator.py
  app/agent/prompts.py
  app/agent/tools.py
  app/services/foundry.py
  app/services/serper.py
frontend/
  src/App.tsx
  src/components/Chat.tsx
  src/components/HotelCards.tsx
  src/api/client.ts
```
