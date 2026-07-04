CREATE TABLE IF NOT EXISTS email_subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  confirm_token TEXT NOT NULL UNIQUE,
  unsubscribe_token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  confirmed_at TEXT,
  unsubscribed_at TEXT,
  last_sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_email_subscribers_email
ON email_subscribers(email);

CREATE INDEX IF NOT EXISTS idx_email_subscribers_status
ON email_subscribers(status);

CREATE INDEX IF NOT EXISTS idx_email_subscribers_confirm_token
ON email_subscribers(confirm_token);

CREATE INDEX IF NOT EXISTS idx_email_subscribers_unsubscribe_token
ON email_subscribers(unsubscribe_token);
