# Backend API

ここから FastAPI backend を一から育てます。

最初の目標は `GET /health` だけです。

## Run

```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 4000
```

## Check

```bash
curl http://127.0.0.1:4000/health
```

