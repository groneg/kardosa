-- PostgreSQL-compatible Token table creation

CREATE TABLE IF NOT EXISTS token (
    id SERIAL PRIMARY KEY,
    token VARCHAR(36) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    expiration TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_token_token ON token (token);
