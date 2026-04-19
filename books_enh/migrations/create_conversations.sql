-- Migration: Add conversation and message tables
-- Run this SQL script in your Supabase SQL editor

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversation (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL REFERENCES member(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversation_member_id ON conversation(member_id);
CREATE INDEX idx_conversation_updated_at ON conversation(updated_at DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    model_used VARCHAR(100),
    provider_used VARCHAR(50),
    token_usage JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);

-- Create conversation summaries table
CREATE TABLE IF NOT EXISTS conversationsummary (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    summary_content TEXT NOT NULL,
    messages_summarized INTEGER NOT NULL DEFAULT 0,
    model_used VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_summary_conversation_id ON conversationsummary(conversation_id);
CREATE INDEX idx_summary_created_at ON conversationsummary(created_at DESC);

-- Add updated_at trigger for conversations
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
BEFORE UPDATE ON conversation
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
