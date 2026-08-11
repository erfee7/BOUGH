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
            <button @click="toggleDevPrompt" class="btn-icon toggle-dev-btn" :class="{ 'active': showDevPrompt }" title="Toggle Developer Prompt">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.terminal"></svg>
            </button>
        </div>

        <div class="input-container">
            <textarea 
                ref="textareaRef"
                :value="modelValue" 
                @input="handleInput"
                @keydown.enter.exact.prevent="handleSend"
                placeholder="Type a message... (Enter to send)"
            ></textarea>
            <button v-if="!isStreaming" @click="handleSend" :disabled="!modelValue.trim()" class="send-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.send"></svg>
            </button>
            <button v-else @click="emit('cancel')" class="stop-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.square"></svg>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PromptSelector from './prompts/PromptSelector.vue';
import { useAutoResizeTextarea } from './useAutoResizeTextarea';
import { ICONS } from '@/icons';

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

function toggleDevPrompt() {
    showDevPrompt.value = !showDevPrompt.value;
    // If hiding the panel, clear the prompt text so it doesn't get sent invisibly
    if (!showDevPrompt.value) {
        emit('update:developerPrompt', '');
    }
}

function handleSend() {
    emit('send');
    showDevPrompt.value = false;
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

.toggle-dev-btn.active {
    background: var(--bg-tertiary);
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}

.input-container {
    display: flex;
    align-items: flex-end;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.input-container:focus-within {
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.input-container textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
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

.send-btn, .stop-btn {
    border: none;
    border-radius: var(--radius-md);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 36px;
    width: 36px;
    margin-left: 8px;
    transition: background-color 0.2s, transform 0.1s, opacity 0.2s;
}

.send-btn {
    background: var(--accent-blue);
}

.send-btn:hover:not(:disabled) {
    background: var(--accent-blue-hover);
    transform: translateY(-1px);
}

.send-btn:disabled {
    background: var(--bg-tertiary);
    cursor: not-allowed;
    opacity: 0.7;
}

.stop-btn {
    background: var(--accent-red);
}

.stop-btn:hover {
    background: var(--accent-red-hover);
    transform: translateY(-1px);
}
</style>