CREATE TABLE IF NOT EXISTS email_post_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  neutral_id TEXT NOT NULL UNIQUE,
  post_slug TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_email_post_links_neutral_id
ON email_post_links(neutral_id);

CREATE INDEX IF NOT EXISTS idx_email_post_links_post_slug
ON email_post_links(post_slug);
