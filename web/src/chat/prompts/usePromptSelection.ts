import { ref, computed, onMounted, watch, type Ref } from 'vue';
import { usePromptStore } from '@/chat/stores/prompt';
import { Prompt } from '@/types';
import { loadLocalConfig, updateLocalConfig } from '../persistence';

export function usePromptSelection(
    role: 'system' | 'developer', 
    modelValue: Ref<string>, 
    updateModelValue: (val: string) => void
) {
    const promptStore = usePromptStore();

    onMounted(async () => {
        await promptStore.fetchPrompts();

        if (modelValue.value) {
            // Content already present (e.g., view remounted): honest display
            selectedMode.value = 'custom';
            return;
        }

        // Boot-apply is a system-prompt preference only; developer panel stays ephemeral
        if (role !== 'system') return;
        const savedId = loadLocalConfig().promptId;
        const prompt = savedId ? filteredPrompts.value.find(p => p.id === savedId) : undefined;
        if (prompt) {
            selectedMode.value = prompt.id;
            updateModelValue(prompt.content);
        }
        // Unknown id or fetch failure: leave at 'none', record untouched
    });

    const filteredPrompts = computed(() => {
        return promptStore.prompts.filter((p: Prompt) => p.role === role);
    });

    const selectedMode = ref<string>('none');

    const placeholderText = computed(() => {
        return selectedMode.value === 'none' 
            ? 'No prompt selected. Start typing to use a custom prompt...' 
            : 'Write a custom prompt...';
    });

    // If parent clears the modelValue (e.g., after send), reset to 'none'
    watch(modelValue, (newVal) => {
        if (!newVal && selectedMode.value !== 'custom') {
            selectedMode.value = 'none';
        }
    });

    function onSelectChange() {
        if (selectedMode.value === 'none') {
            updateModelValue('');
        } else if (selectedMode.value === 'custom') {
            return; // Content stays as-is; user types into the textarea
        } else {
            const selected = filteredPrompts.value.find(p => p.id === selectedMode.value);
            if (selected) {
                updateModelValue(selected.content);
            }
        }
        if (role === 'system') {
            const isPromptId = selectedMode.value !== 'none' && selectedMode.value !== 'custom';
            updateLocalConfig({ promptId: isPromptId ? selectedMode.value : null });
        }
    }

    function handleInput(event: Event) {
        const value = (event.target as HTMLTextAreaElement).value;
        if (selectedMode.value === 'none' && value.length > 0) {
            selectedMode.value = 'custom';
        }
        updateModelValue(value);
    }

    return {
        filteredPrompts,
        selectedMode,
        placeholderText,
        onSelectChange,
        handleInput
    };
}