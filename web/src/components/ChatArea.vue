<template>
    <div class="chat-container">
        <MessageList :messages="messages" />
        <InputArea 
            :modelValue="modelValue" 
            @update:modelValue="emit('update:modelValue', $event)"
            @send="emit('send')"
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
    isStreaming: boolean 
}>();
const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'send'): void 
}>();
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}
</style>