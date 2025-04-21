CREATE TABLE IF NOT EXISTS token (
    id INTEGER PRIMARY KEY,
    token VARCHAR(36) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    expiration DATETIME NOT NULL,
    is_revoked BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE INDEX IF NOT EXISTS ix_token_token ON token (token);
