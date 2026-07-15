<template>
    <div class="message-row" :class="{ 'user-role': message.role === 'user', 'assistant-role': message.role === 'assistant' }">
        <div class="message-bubble" :class="{ 'streaming': message.status === 'streaming', 'error': message.status === 'error' }">
            <span v-if="message.content">{{ message.content }}</span>
            <span v-else-if="message.status === 'pending' || message.status === 'streaming'" class="placeholder">...</span>
            <span v-else>Empty</span>
            
            <span v-if="message.status === 'streaming'" class="cursor">▋</span>
        </div>
    </div>
</template>

<script setup lang="ts">

import { Message } from '../types'; 

defineProps<{ message: Message }>();
</script>

<style scoped>
.message-row {
    display: flex;
    margin: 10px 0;
    width: 100%;
}

.user-role {
    justify-content: flex-end;
}

.assistant-role {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 70%;
    padding: 10px 15px;
    border-radius: 12px;
    font-family: sans-serif;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.user-role .message-bubble {
    background-color: #007bff;
    color: white;
}

.assistant-role .message-bubble {
    background-color: #f1f1f1;
    color: black;
}

.message-bubble.error {
    background-color: #ffcccc;
    color: #cc0000;
    border: 1px solid #cc0000;
}

.cursor {
    animation: blink 1s step-end infinite;
    margin-left: 2px;
}

@keyframes blink {
    0%, 100% { opacity: 0; }
    50% { opacity: 1; }
}
</style>