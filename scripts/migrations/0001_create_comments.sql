CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_slug TEXT NOT NULL,
  parent_id INTEGER,
  author_name TEXT NOT NULL,
  content TEXT NOT NULL,
  visitor_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'visible',
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (parent_id) REFERENCES comments(id)
);

CREATE INDEX IF NOT EXISTS idx_comments_post
  ON comments (post_slug, status, created_at);

CREATE INDEX IF NOT EXISTS idx_comments_visitor
  ON comments (visitor_hash, created_at);
