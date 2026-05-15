# Intergalactic Cargo Portal - Python Backend

Same Task 1 functionality implemented in Python.

## Features
- Flask backend with SQLite
- `POST /signup`
- `POST /login`
- `POST /api/upload` (Admin only, multipart `.txt` upload)
- `GET /api/cargo` (authenticated users)
- JWT auth
- Auto role assignment rule:
  - `@nebula-corp.com` -> `Admin`
  - otherwise -> `Standard`
- Upload processing rules:
  - if `DESTINATION` contains `Sector-7`, weight is multiplied by `1.45`
  - final weight is rounded to nearest integer
  - rows with prime rounded weights are skipped

## Setup
1. Create virtual environment and activate it:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create env file:
   - Copy `.env.example` to `.env`
4. Run:
   - `python -m app.app`

Server default: `http://localhost:5000`

## Sample payloads

### Signup (creates Admin)
```json
{
  "name": "Nova Prime",
  "email": "nova@nebula-corp.com",
  "password": "StrongPass123!"
}
```

### Login
```json
{
  "email": "nova@nebula-corp.com",
  "password": "StrongPass123!"
}
```

## Task 2 endpoints

### Upload manifest (Admin only)
- Endpoint: `POST /api/upload`
- Headers: `Authorization: Bearer <jwt>`
- Body: `form-data` with key `file` and value `manifest.txt`

Expected manifest format: text file with header containing at least `DESTINATION` and `WEIGHT`.
Supported delimiters: comma, pipe (`|`), tab.

### Fetch cargo
- Endpoint: `GET /api/cargo`
- Headers: `Authorization: Bearer <jwt>`
