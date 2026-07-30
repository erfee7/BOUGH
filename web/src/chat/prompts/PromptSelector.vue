<template>
    <div class="prompt-selector">
        <div class="selector-header">
            <select v-model="selectedMode" @change="onSelectChange" class="prompt-select">
                <option value="none">No Prompt</option>
                <option value="custom">Custom</option>
                <option v-for="p in filteredPrompts" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <button @click="emit('openLibrary')" class="manage-btn" title="Manage Prompts">⚙️</button>
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
    background: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 12px;
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
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
    outline: none;
}

.manage-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #94a3b8;
    padding: 4px;
    transition: color 0.2s;
}

.manage-btn:hover {
    color: #f8fafc;
}

.prompt-textarea {
    width: 100%;
    background: transparent;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
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
    border-color: #3b82f6;
}

.prompt-preview {
    width: 100%;
    background: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    min-height: 60px;
    max-height: 120px;
    overflow-y: auto;
    white-space: pre-wrap;
    box-sizing: border-box;
    text-align: left;
}
</style>