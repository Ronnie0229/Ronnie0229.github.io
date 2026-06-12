CREATE TABLE IF NOT EXISTS daily_views (
  view_date TEXT NOT NULL,
  post_slug TEXT NOT NULL,
  view_count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (view_date, post_slug)
);

CREATE INDEX IF NOT EXISTS idx_daily_views_date
  ON daily_views (view_date);
