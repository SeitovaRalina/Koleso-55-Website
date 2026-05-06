-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create indexes for performance
-- These will be created by SQLAlchemy models, but here for reference
