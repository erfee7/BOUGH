import { ref } from 'vue';
import { useConversations } from './useConversations';
import { ConversationSummary } from '../types';

export function useTitleEdit() {
    const { conversations, updateTitle } = useConversations();

    const editingId = ref<string | null>(null);
    const editText = ref<string>('');

    function startEditing(conv: ConversationSummary) {
        editingId.value = conv.id;
        editText.value = conv.title || '';
    }

    function saveEdit() {
        if (editingId.value) {
            const conv = conversations.value.find(c => c.id === editingId.value);
            if (conv && (conv.title || '') !== editText.value.trim()) {
                updateTitle(editingId.value, editText.value);
            }
            editingId.value = null;
        }
    }

    function cancelEdit() {
        editingId.value = null;
        editText.value = '';
    }

    return {
        editingId,
        editText,
        startEditing,
        saveEdit,
        cancelEdit
    };
}