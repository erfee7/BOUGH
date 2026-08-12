export interface ConversationSummary {
    id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: string;
    parent_id: string | null;
    role: 'system' | 'developer' | 'user' | 'assistant';
    content: string | null;
    reasoning?: string | null;
    status: 'pending' | 'streaming' | 'complete' | 'error' | 'canceled';
    creation_data?: any;
    error_data?: any;
    metadata?: any;
    created_at: string;
}

export interface Prompt {
    id: string;
    name: string;
    content: string;
    role: 'system' | 'developer';
    description: string | null;
    created_at: string;
    updated_at: string;
}

export interface CustomParam {
    id: string;
    key: string;
    rawValue: string;
}

export interface GenerationPayload {
    model?: string;
    parameters?: Record<string, unknown>;
}

export interface GenerationPreset {
    id: string;
    name: string;
    model: string | null;
    parameters: Record<string, any>;
    created_at: string;
    updated_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
}