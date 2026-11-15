# STUDENTHUB — Laboratory Activity 9

## Files
- `app.py`: Flask routes, CRUD API, partner GET/POST integration.
- `init_db.py`: creates/migrates SQLite table and seeds records only if empty.
- `templates/index.html`: responsive dashboard and working UI.
- `requirements.txt`: Python dependencies.
- `Procfile`: Render start command.

## Run in Codespaces
```bash
python -m pip install -r requirements.txt
python init_db.py
python app.py
```
Open port 5000 when Codespaces prompts you.

## Partner API
The default partner endpoint is:
`https://jasminerose-2.onrender.com/api/students`

Set `PARTNER_API_URL` in your hosting environment if your classmate uses a different endpoint. The partner app must support GET and POST at `/api/students`.

## Render
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add environment variable `PARTNER_API_URL` with the partner's full `/api/students` URL.

SQLite files on many hosted platforms may be ephemeral; use a persistent disk or managed database if records must survive redeployments.
