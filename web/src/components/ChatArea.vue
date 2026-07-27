<template>
    <div class="chat-container">
        <MessageList :messages="messages" />
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

const props = defineProps<{ 
    messages: Message[], 
    modelValue: string, 
    isStreaming: boolean,
    developerPrompt: string
}>();

const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'update:developerPrompt', value: string): void,
    (e: 'send'): void,
    (e: 'openLibrary'): void
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