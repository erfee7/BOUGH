-- db/init.sql

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT, -- Nullable, represents an untitled conversation
    active_leaf_id UUID, -- Tracks the currently visible end of the chat tree
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Messages Table (Adjacency List for Rooted Tree)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system', 'developer', 'user', 'assistant', 'tool')),
    parent_id UUID REFERENCES messages(id) ON DELETE CASCADE, -- Nullable, null means it's a root message
    content TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'streaming', 'complete', 'error')),
    error_data JSONB,   -- Stores raw provider error if status = 'error'
    metadata JSONB,     -- Stores generation stats/costs if status = 'complete'
    creation_data JSONB,    -- Stores the generation config used for this message
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Prompts Table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('system', 'developer')),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- Indexes for fast traversal
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages (parent_id);
CREATE INDEX IF NOT EXISTS idx_prompts_role ON prompts (role);