# Phone Repair Tracker

A simple FastAPI + SQLite web app for tracking phone/device repairs and customers, with optional Google Contacts import.

## Features
- Customers: name, email, phone, created date
- Repairs: customer, device type, repair type, price, received/completed dates, notes
- HTML UI with basic styling
- Google OAuth (People API) to import contacts (names, email, phone)

## Setup
1. Create virtualenv and install deps
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Copy env and set values
```bash
cp .env.example .env
# Set SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
# Keep OAUTH_REDIRECT_URI matching your Google OAuth credentials
```
3. Run the app
```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Google OAuth setup
- Create OAuth 2.0 Client ID (Web application) in Google Cloud Console
- Authorized redirect URI: http://localhost:8000/auth/google/callback
- Enable People API
- Put `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` in `.env`

## Notes
- SQLite DB is created at `app.db` in project root by default.
- You can change `DATABASE_URL` in `.env`.
