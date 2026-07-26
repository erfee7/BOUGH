import { ref, computed, onMounted, watch, type Ref } from 'vue';
import { usePrompts } from './usePrompts';
import { Prompt } from '../types';

export function usePromptSelection(
    role: 'system' | 'developer', 
    modelValue: Ref<string>, 
    updateModelValue: (val: string) => void
) {
    const { prompts, fetchPrompts } = usePrompts();

    onMounted(() => {
        fetchPrompts(role);
    });

    const filteredPrompts = computed(() => {
        return prompts.value.filter((p: Prompt) => p.role === role);
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
            return; 
        } else {
            const selected = filteredPrompts.value.find(p => p.id === selectedMode.value);
            if (selected) {
                updateModelValue(selected.content);
            }
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