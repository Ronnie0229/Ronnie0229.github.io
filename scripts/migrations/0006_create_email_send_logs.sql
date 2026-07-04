CREATE TABLE IF NOT EXISTS email_send_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_send_id INTEGER NOT NULL,
  subscriber_id INTEGER NOT NULL,
  email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  resend_id TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  sent_at TEXT,
  FOREIGN KEY (post_send_id) REFERENCES email_post_sends(id),
  FOREIGN KEY (subscriber_id) REFERENCES email_subscribers(id)
);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_post_send_id
ON email_send_logs(post_send_id);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_subscriber_id
ON email_send_logs(subscriber_id);

CREATE INDEX IF NOT EXISTS idx_email_send_logs_status
ON email_send_logs(status);
