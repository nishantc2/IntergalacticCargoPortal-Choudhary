CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('Admin', 'Standard')),
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cargo_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  shipment_id TEXT,
  origin TEXT,
  destination TEXT NOT NULL,
  weight_kg INTEGER NOT NULL,
  uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
);
