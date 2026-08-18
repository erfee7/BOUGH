<template>
    <div class="prompt-selector">
        <div class="selector-header">
            <select v-model="selectedMode" @change="onSelectChange" class="prompt-select">
                <option value="none">No Prompt</option>
                <option value="custom">Custom</option>
                <option v-for="p in filteredPrompts" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <button @click="emit('openLibrary')" class="btn-icon" title="Manage Prompts">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.book_open"></svg>
            </button>
        </div>
        
        <!-- Textarea is always available for none/custom -->
        <textarea 
            v-if="selectedMode === 'none' || selectedMode === 'custom'"
            :value="modelValue" 
            @input="handleInput"
            class="prompt-textarea"
            :placeholder="placeholderText"
        ></textarea>
        
        <!-- Read-only preview for selected presets -->
        <div v-else class="prompt-preview">
            {{ modelValue }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { toRef } from 'vue';
import { usePromptSelection } from './usePromptSelection';
import { ICONS } from '@/icons';

const props = defineProps<{ 
    role: 'system' | 'developer', 
    modelValue: string 
}>();
const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'openLibrary'): void 
}>();

const modelValueRef = toRef(props, 'modelValue');
const updateModelValue = (val: string) => emit('update:modelValue', val);

const { filteredPrompts, selectedMode, placeholderText, onSelectChange, handleInput } = usePromptSelection(
    props.role, 
    modelValueRef, 
    updateModelValue
);
</script>

<style scoped>
.prompt-selector {
    margin-bottom: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 8px;
}

.selector-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.prompt-select {
    flex: 1;
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 6px;
    font-size: 13px;
    outline: none;
    cursor: pointer;
}

.prompt-select:focus {
    border-color: var(--accent-blue);
}

.prompt-textarea {
    width: 100%;
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 8px;
    font-family: inherit;
    font-size: 13px;
    resize: vertical;
    min-height: 60px;
    max-height: 120px;
    outline: none;
    box-sizing: border-box;
}

.prompt-textarea:focus {
    border-color: var(--accent-blue);
}

.prompt-preview {
    width: 100%;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 8px;
    font-size: 13px;
    min-height: 60px;
    max-height: 120px;
    overflow-y: auto;
    white-space: pre-wrap;
    box-sizing: border-box;
    text-align: left;
}

@media (max-width: 768px) {
    .modal-content {
        width: 100%;
        max-width: none;
        height: 100%;
        max-height: none;
        border-radius: 0;
        border: none;
    }
}
</style>