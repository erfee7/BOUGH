import { ref } from 'vue';
import { useConversations } from './useConversations';
import { useMessages } from './useMessages';

export function useChatEngine() {
    const { 
        currentConversationId, 
        fetchAllConversations, 
        createConversation, 
        selectConversation, 
        generateTitle 
    } = useConversations();
    
    const { 
        messages, 
        activeLeafId, 
        isStreaming, 
        loadConversation, 
        sendMessage, 
        clearMessages, 
        stopStreaming 
    } = useMessages();

    const inputText = ref('');
    const systemPrompt = ref('');
    const developerPrompt = ref('');
    const isPromptLibraryVisible = ref(false);

    // Used to bypass the watcher when transitioning from "new chat" to "chat created"
    // to prevent the watcher from fetching the DB and wiping the in-flight user message.
    let skipWatch = false;

    function initialize() {
        fetchAllConversations();
    }

    function handleNavigation(newId: string | null) {
        stopStreaming();
        if (skipWatch) {
            skipWatch = false;
            return;
        }
        if (newId) {
            loadConversation(newId);
        } else {
            clearMessages();
            systemPrompt.value = ''; // Reset system prompt for new chat
        }
    }

    async function send() {
        if (!inputText.value.trim() || isStreaming.value) return;
        const text = inputText.value;
        inputText.value = '';
        
        if (!currentConversationId.value) {
            // Use the selected/written system prompt (empty string if null)
            const sysPrompt = systemPrompt.value.trim() || null;
            const result = await createConversation(null, sysPrompt);
            if (!result) return;
            
            skipWatch = true; 
            selectConversation(result.conversationId);
            activeLeafId.value = result.rootMessageId;
            
            const devPrompt = developerPrompt.value.trim() || null;
            const userMsgId = await sendMessage(text, devPrompt);
            
            if (userMsgId && currentConversationId.value) {
                generateTitle(currentConversationId.value, false);
            }
        } else {
            const devPrompt = developerPrompt.value.trim() || null;
            await sendMessage(text, devPrompt);
        }
        
        // Clear developer prompt after sending
        developerPrompt.value = '';
    }

    async function cancel() {
        if (!activeLeafId.value || !isStreaming.value) return;
        const messageId = activeLeafId.value;
        
        // 1. Abort the local SSE listener
        stopStreaming();
        
        // 2. Update local state immediately so UI unlocks
        const msgIndex = messages.value.findIndex(m => m.id === messageId);
        if (msgIndex !== -1) {
            messages.value[msgIndex].status = 'canceled';
        }
        
        // 3. Tell the backend to stop the LLM and save partial content
        try {
            await fetch(`/api/chat/messages/${messageId}/cancel`, { method: 'POST' });
        } catch (error) {
            console.error("Error canceling message:", error);
        }
    }

    return {
        currentConversationId,
        messages,
        isStreaming,
        inputText,
        systemPrompt,
        developerPrompt,
        isPromptLibraryVisible,
        initialize,
        handleNavigation,
        send,
        cancel
    };
}