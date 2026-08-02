# travel-planner-service

FastAPI scaffold for a multi-agent travel planner.

## Run

```bash
uvicorn app.main:app --reload
```

## Routes

- `POST /api/v1/plan-trip`
- `GET /api/v1/trips/{trip_id}`
- `GET /health`
