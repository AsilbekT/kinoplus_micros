CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    email VARCHAR(255) UNIQUE, -- Optional, must be unique if provided
    phone_number VARCHAR(15) UNIQUE, -- Optional, must be unique if provided
    name VARCHAR(100), -- Optional, not unique
    google_id VARCHAR(100) UNIQUE, -- Optional, must be unique if provided
    apple_id VARCHAR(100) UNIQUE, -- Optional, must be unique if provided
    auth_type VARCHAR(30), -- Optional, not unique
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatically set on row creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Automatically set on row creation
);

-- Create a trigger to update the `updated_at` field on update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the `users` table
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users (phone_number);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_apple_id ON users (apple_id);

----------- sessions
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY, -- Auto-incrementing primary key
    user_id INT, -- Foreign key to the users table
    device_name VARCHAR(100), -- Optional
    token VARCHAR(255) UNIQUE NOT NULL, -- Required, must be unique
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatically set on row creation
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatically set on row creation

    -- Foreign key constraint
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Create a trigger to update the `updated_at` field on update
CREATE OR REPLACE FUNCTION update_sessions_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the `sessions` table
CREATE TRIGGER set_sessions_updated_at
BEFORE UPDATE ON sessions
FOR EACH ROW
EXECUTE FUNCTION update_sessions_updated_at_column();

-- Index for faster queries on user_id
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);