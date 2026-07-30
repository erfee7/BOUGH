<template>
    <div class="chat-container">
        <MessageList 
            :activePath="activePath" 
            :allMessages="messages" 
            :isStreaming="isStreaming"
            :editingMessageId="editingMessageId"
            :editingText="editingText"
            @switch-sibling="(id, dir) => emit('switch-sibling', id, dir)"
            @generate="(id) => emit('generate', id)"
            @start-edit="(msg) => emit('start-edit', msg)"
            @cancel-edit="emit('cancel-edit')"
            @save-edit="(msg, gen) => emit('save-edit', msg, gen)"
            @update:editingText="(val) => emit('update:editingText', val)"
        />
        <InputArea 
            :modelValue="modelValue" 
            @update:modelValue="emit('update:modelValue', $event)"
            :developerPrompt="developerPrompt"
            @update:developerPrompt="emit('update:developerPrompt', $event)"
            @send="emit('send')"
            @openLibrary="emit('openLibrary')"
            :isStreaming="isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue';
import InputArea from './InputArea.vue';
import { Message } from '../types';

defineProps<{ 
    messages: Message[], 
    activePath: Message[],
    modelValue: string, 
    isStreaming: boolean,
    developerPrompt: string,
    editingMessageId: string | null,
    editingText: string
}>();

const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'update:developerPrompt', value: string): void,
    (e: 'send'): void,
    (e: 'openLibrary'): void,
    (e: 'switch-sibling', messageId: string, direction: 'prev' | 'next'): void,
    (e: 'generate', messageId: string): void,
    (e: 'start-edit', message: Message): void,
    (e: 'cancel-edit'): void,
    (e: 'save-edit', message: Message, shouldGenerate: boolean): void,
    (e: 'update:editingText', value: string): void
}>();
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    margin: 0 auto;
}
</style>