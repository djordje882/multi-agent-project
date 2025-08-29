-- Initialize payroll database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Time entries table
CREATE TABLE IF NOT EXISTS time_entries (
    id SERIAL PRIMARY KEY,
    punch_time TIMESTAMPTZ NOT NULL,
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('in', 'out', 'sick', 'vacation')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 15.00,
    timezone VARCHAR(50) DEFAULT 'UTC',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_time_entries_punch_time ON time_entries(punch_time);
CREATE INDEX IF NOT EXISTS idx_time_entries_type ON time_entries(entry_type);

-- Insert default user settings
INSERT INTO user_settings (hourly_rate) 
VALUES (15.00) 
ON CONFLICT (id) DO NOTHING;