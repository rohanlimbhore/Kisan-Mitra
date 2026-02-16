# Krishi Mitra

Production-ready Flask web platform for an AgriTech startup offering AI assistant, crop diagnosis, community sharing, and government scheme guidance.

## Tech Stack
- Flask + SQLAlchemy
- SQLite
- Vanilla HTML/CSS/JS (responsive, mobile-first)
- OpenAI-compatible API integration via `AI_API_KEY`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Environment Variables
Create `.env` file:
```env
SECRET_KEY=replace-in-production
AI_API_KEY=your-provider-api-key
AI_MODEL=gpt-4o-mini
```

> API key comment location: `app/services/ai_service.py` (`_headers` function).

## Deployment
Use Gunicorn in production:
```bash
gunicorn -w 3 -b 0.0.0.0:8000 run:app
```
