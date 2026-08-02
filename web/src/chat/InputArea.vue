<template>
    <div class="input-area">
        <div v-if="showDevPrompt" class="dev-prompt-panel">
            <PromptSelector 
                role="developer" 
                :modelValue="developerPrompt" 
                @update:modelValue="emit('update:developerPrompt', $event)"
                @openLibrary="emit('openLibrary')"
            />
        </div>
        
        <div class="action-bar">
            <button @click="showDevPrompt = !showDevPrompt" class="toggle-dev-btn" :class="{ 'active': showDevPrompt }" title="Toggle Developer Prompt">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.terminal"></svg>
            </button>
        </div>

        <div class="input-container">
            <textarea 
                ref="textareaRef"
                :value="modelValue" 
                @input="handleInput"
                @keydown.enter.exact.prevent="emit('send')"
                placeholder="Type a message... (Enter to send)"
            ></textarea>
            <button v-if="!isStreaming" @click="emit('send')" :disabled="!modelValue.trim()">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.send"></svg>
            </button>
            <button v-else @click="emit('cancel')" class="stop-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.stop"></svg>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PromptSelector from './prompts/PromptSelector.vue';
import { useAutoResizeTextarea } from './useAutoResizeTextarea';
import { ICONS } from '../icons';

const props = defineProps<{ 
    modelValue: string, 
    isStreaming: boolean,
    developerPrompt: string 
}>();

const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'update:developerPrompt', value: string): void,
    (e: 'send'): void,
    (e: 'cancel'): void,
    (e: 'openLibrary'): void 
}>();

const showDevPrompt = ref(false);

const { textareaRef, adjustHeight } = useAutoResizeTextarea(() => props.modelValue);

function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    emit('update:modelValue', target.value);
    adjustHeight();
}
</script>

<style scoped>
.input-area {
    padding: 20px 2% 32px;
}

@media (max-width: 1024px) {
    .input-area {
        padding: 20px 16px 32px;
    }
}

.dev-prompt-panel {
    margin-bottom: 12px;
}

.action-bar {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 8px;
}

.toggle-dev-btn {
    background: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    border-radius: 6px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
}

.toggle-dev-btn:hover {
    color: #f8fafc;
    border-color: #475569;
}

.toggle-dev-btn.active {
    background: #334155;
    color: #3b82f6;
    border-color: #3b82f6;
}

.input-container {
    display: flex;
    align-items: flex-end;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.input-container:focus-within {
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.input-container textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: #f8fafc;
    font-family: inherit;
    font-size: 15px;
    line-height: 1.5;
    max-height: 200px;
    min-height: 24px;
    padding: 0 8px;
    resize: none;
    outline: none;
    overflow-y: auto; /* Show scrollbar when content exceeds max height */
}

.input-container button {
    background: #3b82f6;
    border: none;
    border-radius: 10px;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 36px;
    width: 36px;
    margin-left: 8px;
    transition: background-color 0.2s, transform 0.1s;
}

.input-container button:hover:not(:disabled) {
    background: #2563eb;
    transform: translateY(-1px);
}

.input-container button:disabled {
    background: #475569;
    cursor: not-allowed;
    opacity: 0.7;
}

.input-container button.stop-btn {
    background: #ef4444;
}

.input-container button.stop-btn:hover {
    background: #dc2626;
    transform: translateY(-1px);
}
</style>