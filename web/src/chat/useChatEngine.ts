import { ref, watch } from 'vue';
import { useConversationStore } from './stores/conversation';
import { useMessageStore } from './stores/message';
import { useAttachmentStore } from './stores/attachment';
import { loadLocalConfig, updateLocalConfig } from './persistence';

export function useChatEngine() {
    const conversationStore = useConversationStore();
    const messageStore = useMessageStore();
    const attachmentStore = useAttachmentStore();

    const inputText = ref('');
    const systemPrompt = ref('');
    const developerPrompt = ref('');
    const isPromptLibraryVisible = ref(false);

    async function initialize() {
        await conversationStore.fetchAllConversations();
        // Read after the fetch: a click-to-new-chat during boot must not be overridden
        const savedId = loadLocalConfig().conversationId;
        if (savedId && conversationStore.conversations.some(c => c.id === savedId)) {
            await navigate(savedId);
        }
    }

    // Persist mirror: also covers deleteConversation's direct null assignment
    watch(() => conversationStore.currentConversationId, (id) => {
        updateLocalConfig({ conversationId: id });
    });

    // Explicit navigation function replaces the implicit watcher
    async function navigate(id: string | null) {
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
        const attachmentIds = [...attachmentStore.readyAttachmentIds];
        if ((!inputText.value.trim() && attachmentIds.length === 0) || messageStore.isStreaming || attachmentStore.hasBlockingDrafts) return;
        const text = inputText.value;
        inputText.value = '';
        
        let sentOk = false;
        if (!conversationStore.currentConversationId) {
            // Use the selected/written system prompt (empty string if null)
            const sysPrompt = systemPrompt.value.trim() || null;
            const result = await conversationStore.createConversation(null, sysPrompt);
            if (!result) return;
            
            // Explicitly navigate to the new conversation to hydrate the root system message
            // This guarantees the root message is in the local array before we append the user message.
            await navigate(result.conversationId);
            
            const devPrompt = developerPrompt.value.trim() || null;
            const userMsgId = await messageStore.sendMessage(text, devPrompt, attachmentIds);
            
            if (userMsgId && conversationStore.currentConversationId) {
                conversationStore.generateTitle(conversationStore.currentConversationId, false);
            }
            sentOk = !!userMsgId;
        } else {
            const devPrompt = developerPrompt.value.trim() || null;
            sentOk = !!(await messageStore.sendMessage(text, devPrompt, attachmentIds));
        }

        if (sentOk) attachmentStore.clearDrafts(); // On failure: keep drafts for a retry send
        developerPrompt.value = ''; // Clear developer prompt after sending
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