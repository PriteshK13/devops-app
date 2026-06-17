# Lumina Events — Microservices Event Management Platform

A modular, containerized event management application built with Python microservices, PostgreSQL (AWS RDS compatible), and Docker.

## Architecture

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌─────────────────────┐
│  Frontend Service   │────▶│  Estimation Engine       │────▶│  PostgreSQL (RDS)   │
│  Flask :5000        │     │  FastAPI :8001           │     │  :5432              │
│  Portfolio + Form   │     │  POST /api/estimate      │     │                     │
│  AI Chat Sidebar    │────▶│                          │     └─────────────────────┘
└─────────────────────┘     └──────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Chatbot Service    │
│  FastAPI :8002      │
│  POST /api/chatbot  │
└─────────────────────┘
```

## Services

| Service | Port | Framework | Description |
|---------|------|-----------|-------------|
| `frontend-service` | 5000 | Flask | Portfolio UI, inquiry form, AI chat panel |
| `estimation-service` | 8001 | FastAPI | Budget-based planning engine + DB persistence |
| `chatbot-service` | 8002 | FastAPI | Rule-based NLP assistant (LLM-ready) |
| `postgres` | 5432 | PostgreSQL 16 | Shared database |

## Quick Start

```bash
# Build and start all services
docker compose up --build

# Seed event catalog (optional, after stack is up)
docker compose exec estimation-service python /app/scripts/seed_catalog.py
```

Open **http://localhost:5000** in your browser.

## API Endpoints

### Estimation Engine — `POST /api/estimate`

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "event_type": "wedding",
  "budget": 15000,
  "budget_currency": "USD",
  "location": "Mumbai, India",
  "special_requirements": "Vegetarian menu"
}
```

**Response:** `Status`, `EstimatedCostBreakdowns`, `SuggestedTimelinePlan`, `TotalEstimatedCost`, `GeneratedPlanText`

**Budget tiers:**
- **Low:** ≤ $5,000 / ₹4.15L — standard venues & decor
- **Medium:** $5K–$25K / ₹4.15L–₹20.75L — premium venues, catering, photography
- **High/Luxury:** > $25K / ₹20.75L — 5-star venues, celebrity hosts, drone coverage

### Chatbot — `POST /api/chatbot`

```json
{ "message": "What is your cancellation policy?" }
```

## Database Models (SQLAlchemy)

- **User** — `id`, `name`, `email`
- **EventCatalog** — `id`, `event_type`, `base_price`, `description`
- **BookingEstimate** — `id`, `user_id`, `event_type`, `budget`, `location`, `generated_plan`, `total_estimated_cost`

## AWS RDS Configuration

Set `DATABASE_URL` for the estimation service:

```
DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/eventdb
```

## LLM Integration (Future)

Edit `chatbot-service/nlp_engine.py` → `generate_llm_response()` to plug in OpenAI or AWS Bedrock.

## Project Structure

```
project/
├── shared/                  # Shared SQLAlchemy models & DB config
├── frontend-service/        # Flask UI + proxy routes
├── estimation-service/      # FastAPI estimation engine
├── chatbot-service/         # FastAPI chatbot
├── scripts/                 # DB seed utilities
└── docker-compose.yml
```
