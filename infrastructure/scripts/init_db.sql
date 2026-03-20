-- AVAS Database Initialization
-- This runs on first PostgreSQL container startup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes will be managed by SQLAlchemy/Alembic migrations
-- This file is for initial DB-level setup only

SELECT 'AVAS database initialized' AS status;
