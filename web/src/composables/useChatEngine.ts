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
        }
    }

    async function send() {
        if (!inputText.value.trim() || isStreaming.value) return;
        const text = inputText.value;
        inputText.value = '';
        
        if (!currentConversationId.value) {
            const result = await createConversation(null, "You are a helpful assistant.");
            if (!result) return;
            
            skipWatch = true; 
            selectConversation(result.conversationId);
            activeLeafId.value = result.rootMessageId;
            
            const userMsgId = await sendMessage(text);
            
            if (userMsgId && currentConversationId.value) {
                generateTitle(currentConversationId.value, false);
            }
        } else {
            await sendMessage(text);
        }
    }

    return {
        currentConversationId,
        messages,
        isStreaming,
        inputText,
        initialize,
        handleNavigation,
        send
    };
}