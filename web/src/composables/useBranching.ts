import { ref, computed } from 'vue';
import { useMessages } from './useMessages';
import { useConversations } from './useConversations';
import { getActivePath, getSiblingInfo, getMostRecentDescendantLeaf, compareMessages } from '../utils/tree';
import { Message } from '../types';

export function useBranching() {
    const { 
        messages, 
        activeLeafId, 
        isStreaming, 
        stopStreaming, 
        startStreaming, 
        generateMessage, 
        appendMessage 
    } = useMessages();
    
    const { 
        currentConversationId, 
        updateActiveLeaf 
    } = useConversations();

    const editingMessageId = ref<string | null>(null);
    const editingText = ref('');

    const activePath = computed(() => {
        return getActivePath(messages.value, activeLeafId.value);
    });

    async function switchSibling(messageId: string, direction: 'prev' | 'next') {
        const { count, currentIndex } = getSiblingInfo(messageId, messages.value);
        if (count <= 1) return;

        let targetIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
        if (targetIndex < 0 || targetIndex >= count) return;

        const targetMsg = messages.value.find(m => m.id === messageId);
        if (!targetMsg || !targetMsg.parent_id) return;

        const siblings = messages.value
            .filter(m => m.parent_id === targetMsg.parent_id)
            .sort(compareMessages);
        
        const targetSibling = siblings[targetIndex];
        const targetLeafId = getMostRecentDescendantLeaf(targetSibling.id, messages.value);

        stopStreaming();
        activeLeafId.value = targetLeafId;
        
        if (currentConversationId.value) {
            updateActiveLeaf(currentConversationId.value, targetLeafId);
        }

        const targetLeafMsg = messages.value.find(m => m.id === targetLeafId);
        if (targetLeafMsg && (targetLeafMsg.status === 'pending' || targetLeafMsg.status === 'streaming')) {
            startStreaming(targetLeafId);
        }
    }

    function startEdit(message: Message) {
        editingMessageId.value = message.id;
        editingText.value = message.content || '';
    }

    function cancelEdit() {
        editingMessageId.value = null;
        editingText.value = '';
    }

    async function saveEdit(message: Message, shouldGenerate: boolean) {
        if (!editingText.value.trim() || editingText.value === message.content) {
            cancelEdit();
            return;
        }

        const newMsgId = await appendMessage(message.parent_id!, editingText.value, message.role as 'user' | 'assistant');
        cancelEdit();

        if (newMsgId && shouldGenerate) {
            generateMessage(newMsgId);
        }
    }

    return {
        activePath,
        editingMessageId,
        editingText,
        isStreaming,
        switchSibling,
        startEdit,
        cancelEdit,
        saveEdit,
        generateMessage
    };
}