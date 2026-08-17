-- db/init.sql

-- Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT, -- Nullable, represents an untitled conversation
    active_leaf_id UUID, -- Tracks the currently visible end of the chat tree
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages Table (Adjacency List for Rooted Tree)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system', 'developer', 'user', 'assistant', 'tool')),
    parent_id UUID REFERENCES messages(id) ON DELETE CASCADE, -- Nullable, null means it's a root message
    content TEXT,
    reasoning TEXT, -- Stores the reasoning/thinking process from LLMs
    attachments JSONB NOT NULL DEFAULT '[]', -- Metadata array referencing standalone blobs: [{"id", "mime_type", "filename", "size"}]
    status TEXT NOT NULL CHECK (status IN ('pending', 'streaming', 'complete', 'error', 'canceled')),
    error_data JSONB,   -- Stores raw provider error if status = 'error'
    metadata JSONB,     -- Stores generation stats/costs if status = 'complete'
    creation_data JSONB,    -- Stores the generation config used for this message
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Prompts Table
CREATE TABLE IF NOT EXISTS prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('system', 'developer')),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generation Presets Table
CREATE TABLE IF NOT EXISTS generation_presets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    model TEXT, -- Nullable, NULL means server default
    parameters JSONB NOT NULL DEFAULT '{}', -- Raw wire-shaped bag
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users Table (Account System)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Sessions Table (Stateful Cookie-based Auth)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Attachments Table (Blob Vault)
CREATE TABLE IF NOT EXISTS attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mime_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    size INTEGER NOT NULL, -- In bytes, measured server-side from actual data
    data BYTEA NOT NULL,  -- TOASTed; only read by explicit SELECTs on this column
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast traversal
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent ON messages (parent_id);
CREATE INDEX IF NOT EXISTS idx_prompts_role ON prompts (role);
CREATE INDEX IF NOT EXISTS idx_generation_presets_name ON generation_presets (name);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);