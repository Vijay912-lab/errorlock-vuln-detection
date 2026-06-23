PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS mistakes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  model TEXT NOT NULL,
  sample_id TEXT NOT NULL,
  code TEXT NOT NULL,
  true_vulnerable INTEGER NOT NULL,
  true_cwe TEXT,
  true_location TEXT,
  predicted_vulnerable INTEGER,
  predicted_cwe TEXT,
  predicted_location TEXT,
  predicted_explanation TEXT,
  failure_type TEXT NOT NULL,
  raw_response TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mistakes_model ON mistakes(model);
CREATE INDEX IF NOT EXISTS idx_mistakes_failure ON mistakes(failure_type);
CREATE INDEX IF NOT EXISTS idx_mistakes_cwe ON mistakes(true_cwe);
