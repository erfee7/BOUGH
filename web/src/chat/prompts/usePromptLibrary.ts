import { ref, watch, type Ref } from 'vue';
import { storeToRefs } from 'pinia';
import { usePromptStore } from '@/chat/stores/prompt';
import { Prompt } from '@/types';

export function usePromptLibrary(isVisible: Ref<boolean>) {
    const promptStore = usePromptStore();
    const { prompts } = storeToRefs(promptStore);
    const { fetchPrompts, createPrompt, updatePrompt, deletePrompt } = promptStore;

    const newPrompt = ref({
        name: '',
        role: 'system' as 'system' | 'developer',
        content: '',
        description: ''
    });

    const editingId = ref<string | null>(null);
    const editData = ref({
        name: '',
        content: '',
        description: ''
    });

    watch(isVisible, (visible) => {
        if (visible) {
            fetchPrompts();
        }
    });

    async function handleCreate() {
        if (!newPrompt.value.name || !newPrompt.value.content) return;
        await createPrompt(newPrompt.value);
        newPrompt.value = { name: '', role: 'system', content: '', description: '' };
    }

    function startEditing(p: Prompt) {
        editingId.value = p.id;
        editData.value = { name: p.name, content: p.content, description: p.description || '' };
    }

    function cancelEdit() {
        editingId.value = null;
    }

    async function handleUpdate() {
        if (!editingId.value) return;
        await updatePrompt(editingId.value, editData.value);
        editingId.value = null;
    }

    async function handleDelete(id: string) {
        await deletePrompt(id);
    }

    return {
        prompts,
        newPrompt,
        editingId,
        editData,
        handleCreate,
        startEditing,
        cancelEdit,
        handleUpdate,
        handleDelete
    };
}