import { ref } from 'vue';
import { useConversationStore } from './stores/conversation';
import { useMessageStore } from './stores/message';

export function useChatEngine() {
    const conversationStore = useConversationStore();
    const messageStore = useMessageStore();

    const inputText = ref('');
    const systemPrompt = ref('');
    const developerPrompt = ref('');
    const isPromptLibraryVisible = ref(false);

    function initialize() {
        conversationStore.fetchAllConversations();
    }

    // Explicit navigation function replaces the implicit watcher
    async function navigate(id: string | null) {
        messageStore.stopStreaming();
        
        if (id) {
            conversationStore.selectConversation(id);
            await messageStore.loadConversation(id);
        } else {
            conversationStore.selectConversation(null);
            messageStore.clearMessages();
            systemPrompt.value = ''; // Reset system prompt for new chat
        }
    }

    async function send() {
        if (!inputText.value.trim() || messageStore.isStreaming) return;
        const text = inputText.value;
        inputText.value = '';
        
        if (!conversationStore.currentConversationId) {
            // Use the selected/written system prompt (empty string if null)
            const sysPrompt = systemPrompt.value.trim() || null;
            const result = await conversationStore.createConversation(null, sysPrompt);
            if (!result) return;
            
            // Explicitly navigate to the new conversation to hydrate the root system message
            // This guarantees the root message is in the local array before we append the user message.
            await navigate(result.conversationId);
            
            const devPrompt = developerPrompt.value.trim() || null;
            const userMsgId = await messageStore.sendMessage(text, devPrompt);
            
            if (userMsgId && conversationStore.currentConversationId) {
                conversationStore.generateTitle(conversationStore.currentConversationId, false);
            }
        } else {
            const devPrompt = developerPrompt.value.trim() || null;
            await messageStore.sendMessage(text, devPrompt);
        }
        
        // Clear developer prompt after sending
        developerPrompt.value = '';
    }

    async function cancel() {
        messageStore.cancelGeneration();
    }

    return {
        inputText,
        systemPrompt,
        developerPrompt,
        isPromptLibraryVisible,
        initialize,
        navigate,
        send,
        cancel
    };
}