<template>
    <div class="chat-container">
        <MessageList />
        <InputArea 
            :modelValue="inputText" 
            @update:modelValue="inputText = $event"
            :developerPrompt="developerPrompt"
            @update:developerPrompt="developerPrompt = $event"
            @send="send"
            @openLibrary="emit('openLibrary')"
            :isStreaming="isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue';
import InputArea from './InputArea.vue';
import { useChatEngine } from '../composables/useChatEngine';

const emit = defineEmits<{ 
    (e: 'openLibrary'): void
}>();

const { 
    inputText, 
    developerPrompt, 
    isStreaming, 
    send 
} = useChatEngine();
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