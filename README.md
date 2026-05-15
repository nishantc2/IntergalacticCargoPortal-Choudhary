# Intergalactic Cargo Portal - Python Backend

Same Task 1 functionality implemented in Python.

## Features
- Flask backend with SQLite
- `POST /signup`
- `POST /login`
- `POST /api/upload` (Admin only, multipart `.txt` upload)
- `GET /api/cargo` (authenticated users)
- Frontend dashboard at `/`
- JWT auth
- Auto role assignment rule:
  - `@nebula-corp.com` -> `Admin`
  - otherwise -> `Standard`
- Upload processing rules:
  - if `DESTINATION` contains `Sector-7`, weight is multiplied by `1.45`
  - final weight is rounded to nearest integer
  - rows with prime rounded weights are skipped
- Frontend display rules:
  - Admin sees `File Upload` and cargo weight in `KG`
  - Standard sees no upload control and weight in `LBS`
  - Cargo list sorted heaviest to lightest, with destination `Earth` pinned to bottom
  - Cargo table uses pagination with 5 rows per page
  - Login and Signup are shown as separate switchable views
  - Auth submit buttons show loading spinner and prevent double-submit
  - Logout clears persisted session and resets auth form inputs

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
Frontend: `http://localhost:5000/`

## Task 3 frontend flow
- Open `/` to access Login view.
- Use "Create an account" link to switch to Signup and "Go to login" to switch back.
- After auth:
  - Admin dashboard: upload control + cargo table with `KG`
  - Standard dashboard: cargo table only with `LBS`
- Use `Prev` and `Next` controls below the table to navigate pages (5 rows per page).

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
