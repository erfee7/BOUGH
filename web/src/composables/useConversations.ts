import { ref } from 'vue';
import { ConversationSummary } from '../types';

const conversations = ref<ConversationSummary[]>([]);
const currentConversationId = ref<string | null>(null);

export function useConversations() {
    
    async function fetchAllConversations() {
        try {
            const response = await fetch('/api/chat/conversations');
            if (!response.ok) throw new Error('Failed to fetch conversations');
            conversations.value = await response.json();
        }
        catch (error) {
            console.error("Error fetching conversations:", error);
        }
    }

    async function createConversation(title: string | null = null, systemPrompt: string | null = null): Promise<{ conversationId: string, rootMessageId: string } | null> {
        try {
            const response = await fetch('/api/chat/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, system_prompt: systemPrompt })
            });
            
            if (!response.ok) throw new Error('Failed to create conversation');
            const data = await response.json();
            
            const newConv: ConversationSummary = {
                id: data.conversation.id,
                title: data.conversation.title,
                created_at: data.conversation.created_at
            };
            
            // Add to top of list and select it
            conversations.value.unshift(newConv);
            // We no longer call selectConversation here. 
            // App.vue will handle the state transition to avoid race conditions.
            
            return { 
                conversationId: data.conversation.id, 
                rootMessageId: data.root_message_id 
            };
        } catch (error) {
            console.error("Error creating conversation:", error);
            return null;
        }
    }

    function selectConversation(id: string | null) {
        currentConversationId.value = id;
    }

    return {
        conversations,
        currentConversationId,
        fetchAllConversations,
        createConversation,
        selectConversation
    };
}