export interface ConversationSummary {
    id: string;
    title: string | null;
    created_at: string;
}

export interface Message {
    id: string;
    parent_id: string | null;
    role: 'system' | 'developer' | 'user' | 'assistant';
    content: string | null;
    status: 'pending' | 'streaming' | 'complete' | 'error';
    creation_data?: any;
    error_data?: any;
    metadata?: any;
    created_at: string;
}

// We can also type the SSE events here for clarity
export interface StreamEvent {
    type: 'token' | 'catch_up' | 'done' | 'error';
    content?: string;
    metadata?: any;
    error_data?: any;
}