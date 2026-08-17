import { ref } from 'vue';
import { useMessageStore } from './stores/message';
import { Message } from '@/types';

export function useMessageEdit() {
    const messageStore = useMessageStore();

    const editingMessageId = ref<string | null>(null);
    const editingText = ref('');

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

        const newMsgId = await messageStore.appendMessage(
            message.parent_id!,
            editingText.value,
            message.role as 'user' | 'assistant',
            message.attachments?.map(a => a.id) ?? [] // Files carry through edits unchanged
        );
        cancelEdit();

        if (newMsgId && shouldGenerate) {
            messageStore.generateMessage(newMsgId);
        }
    }

    return {
        editingMessageId,
        editingText,
        startEdit,
        cancelEdit,
        saveEdit
    };
}