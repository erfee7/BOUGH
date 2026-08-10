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

    // Used to bypass the watcher when transitioning from "new chat" to "chat created"
    // to prevent the watcher from fetching the DB and wiping the in-flight user message.
    let skipWatch = false;

    function initialize() {
        conversationStore.fetchAllConversations();
    }

    function handleNavigation(newId: string | null) {
        messageStore.stopStreaming();
        if (skipWatch) {
            skipWatch = false;
            return;
        }
        if (newId) {
            messageStore.loadConversation(newId);
        } else {
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
            
            skipWatch = true; 
            conversationStore.selectConversation(result.conversationId);
            messageStore.activeLeafId = result.rootMessageId;
            
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
        handleNavigation,
        send,
        cancel
    };
}