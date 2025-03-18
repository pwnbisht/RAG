-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- Create custom ENUM type
CREATE TYPE statusenum AS ENUM ('FAILED', 'SUCCESS', 'PROCESSING');

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE
);

-- Create token table
CREATE TABLE IF NOT EXISTS token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    access_token VARCHAR(450) UNIQUE NOT NULL,
    refresh_token VARCHAR(450) NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status statusenum,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create document_chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    content TEXT NOT NULL,
    embedding vector(2048) NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_token_user_status ON token(user_id, status);
CREATE INDEX IF NOT EXISTS idx_document_user ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE USER app_user WITH PASSWORD 'app_password';
GRANT CONNECT ON DATABASE voiceai TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;