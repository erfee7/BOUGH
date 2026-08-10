import { ref, computed } from 'vue';
import { useMessageStore } from './stores/message';
import { useConversationStore } from './stores/conversation';
import { getActivePath, getSiblingInfo, getMostRecentDescendantLeaf, compareMessages } from './branchingUtils';
import { Message } from '@/types';

export function useBranching() {
    const messageStore = useMessageStore();
    const conversationStore = useConversationStore();

    const editingMessageId = ref<string | null>(null);
    const editingText = ref('');

    const activePath = computed(() => {
        return getActivePath(messageStore.messages, messageStore.activeLeafId);
    });

    async function switchSibling(messageId: string, direction: 'prev' | 'next') {
        const { count, currentIndex } = getSiblingInfo(messageId, messageStore.messages);
        if (count <= 1) return;

        let targetIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
        if (targetIndex < 0 || targetIndex >= count) return;

        const targetMsg = messageStore.messages.find(m => m.id === messageId);
        if (!targetMsg || !targetMsg.parent_id) return;

        const siblings = messageStore.messages
            .filter(m => m.parent_id === targetMsg.parent_id)
            .sort(compareMessages);
        
        const targetSibling = siblings[targetIndex];
        const targetLeafId = getMostRecentDescendantLeaf(targetSibling.id, messageStore.messages);

        messageStore.stopStreaming();
        messageStore.activeLeafId = targetLeafId;
        
        if (conversationStore.currentConversationId) {
            conversationStore.updateActiveLeaf(conversationStore.currentConversationId, targetLeafId);
        }

        const targetLeafMsg = messageStore.messages.find(m => m.id === targetLeafId);
        if (targetLeafMsg && (targetLeafMsg.status === 'pending' || targetLeafMsg.status === 'streaming')) {
            messageStore.startStreaming(targetLeafId);
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

        const newMsgId = await messageStore.appendMessage(message.parent_id!, editingText.value, message.role as 'user' | 'assistant');
        cancelEdit();

        if (newMsgId && shouldGenerate) {
            messageStore.generateMessage(newMsgId);
        }
    }

    return {
        activePath,
        editingMessageId,
        editingText,
        switchSibling,
        startEdit,
        cancelEdit,
        saveEdit
    };
}