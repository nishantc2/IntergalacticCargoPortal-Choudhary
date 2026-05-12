# Intergalactic Cargo Portal - Python Backend

Same Task 1 functionality implemented in Python.

## Features
- Flask backend with SQLite
- `POST /signup`
- `POST /login`
- JWT auth
- Auto role assignment rule:
  - `@nebula-corp.com` -> `Admin`
  - otherwise -> `Standard`

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
