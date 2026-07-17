import { ref } from 'vue';
import { ConversationSummary } from '../types';

const conversations = ref<ConversationSummary[]>([]);
const currentConversationId = ref<string | null>(null);
const generatingTitleIds = ref<string[]>([]);

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

    async function updateTitle(id: string, title: string) {
        try {
            const response = await fetch(`/api/chat/conversations/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });
            
            if (!response.ok) throw new Error('Failed to update title');
            
            // Update the local reactive state immediately
            const conv = conversations.value.find(c => c.id === id);
            if (conv) {
                // Normalize empty string to null for local state consistency
                conv.title = title.trim() === '' ? null : title;
            }
        } catch (error) {
            console.error("Error updating title:", error);
        }
    }

    async function generateTitle(id: string, force: boolean = false) {
        if (generatingTitleIds.value.includes(id)) return;
        generatingTitleIds.value = [...generatingTitleIds.value, id];
        
        try {
            const response = await fetch(`/api/chat/conversations/${id}/generate-title`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ force })
            });
            if (!response.ok) throw new Error('Failed to generate title');
            
            const data = await response.json();
            const conv = conversations.value.find(c => c.id === id);
            if (conv) {
                conv.title = data.title;
            }
        } catch (error) {
            console.error("Error generating title:", error);
        } finally {
            generatingTitleIds.value = generatingTitleIds.value.filter(i => i !== id);
        }
    }

    return {
        conversations,
        currentConversationId,
        fetchAllConversations,
        createConversation,
        selectConversation,
        updateTitle,
        generatingTitleIds,
        generateTitle
    };
}