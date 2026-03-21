# BioLearn AI

BioLearn AI is a Flask-based learning platform that generates biotechnology lessons and quizzes using Cohere, with authentication and personalized learning progress tracking.

## Stack
- Backend: Flask, SQLAlchemy, Flask-Login
- AI: Cohere API
- Frontend: HTML templates + static JavaScript/CSS
- Deployment target: Vercel (`@vercel/python`)

## Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create local environment file:
   ```bash
   cp .env.example .env
   ```
3. Fill `.env` with real values (local only).
4. Run app:
   ```bash
   python app.py
   ```

## Environment Variables
Required:
- `FLASK_SECRET_KEY`: Flask session signing secret.
- `COHERE_API_KEY`: Cohere server-side API key.
- `GOOGLE_CLIENT_ID`: Google OAuth client id.
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret.

Optional:
- `FLASK_DEBUG`: `true` or `false` for local debugging.

## Security Notes
- No API keys are hardcoded in source code.
- Secrets are loaded from environment variables only.
- `.env` is ignored by git and must never be committed.
- Frontend calls internal backend routes (`/api/*`), so secret keys are never exposed to the browser.

## Deploying To Vercel
This repo includes `vercel.json` configured to route all traffic through `app.py`.

1. Import this repository in Vercel.
2. In Project Settings -> Environment Variables, add:
   - `FLASK_SECRET_KEY`
   - `COHERE_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `FLASK_DEBUG=false`
3. Deploy.

## Important Secret Hygiene
If any key was previously committed, rotate it immediately:
1. Revoke old key in provider dashboard.
2. Generate a new key.
3. Store only in `.env` (local) and Vercel env settings (production).