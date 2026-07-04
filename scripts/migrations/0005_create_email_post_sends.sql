CREATE TABLE IF NOT EXISTS email_post_sends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_slug TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending',
  subject TEXT NOT NULL,
  recipient_count INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  sent_at TEXT,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_email_post_sends_post_slug
ON email_post_sends(post_slug);

CREATE INDEX IF NOT EXISTS idx_email_post_sends_status
ON email_post_sends(status);
