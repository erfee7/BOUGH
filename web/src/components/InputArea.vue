<template>
    <div class="input-area">
        <div class="input-container">
            <textarea 
                :value="modelValue" 
                @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
                @keydown.enter.exact.prevent="emit('send')"
                placeholder="Type a message... (Enter to send)"
                :disabled="isStreaming"
            ></textarea>
            <button @click="emit('send')" :disabled="isStreaming || !modelValue.trim()">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: string, isStreaming: boolean }>();
const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'send'): void 
}>();
</script>

<style scoped>
.input-area {
    padding: 20px 24px 32px;
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
    max-height: 150px;
    min-height: 24px;
    padding: 0 8px;
    resize: none;
    outline: none;
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
</style>