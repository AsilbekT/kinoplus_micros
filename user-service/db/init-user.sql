-- Create the database if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'user_db') THEN
        EXECUTE 'CREATE DATABASE user_db';
    END IF;
END $$;

-- Connect to the newly created database to create tables
-- Note: this part of the script has to be executed separately if you are using psql commands
\connect user_db;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(15),
    google_id VARCHAR(100),
    apple_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_id ON users (id);
CREATE INDEX IF NOT EXISTS idx_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_apple_id ON users (apple_id);
