<template>
    <div class="chat-container">
        <MessageList />
        <InputArea 
            :modelValue="inputText" 
            @update:modelValue="inputText = $event"
            :developerPrompt="developerPrompt"
            @update:developerPrompt="developerPrompt = $event"
            @send="send"
            @cancel="cancel"
            @openLibrary="emit('openLibrary')"
            :isStreaming="messageStore.isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue';
import InputArea from './InputArea.vue';
import { useMessageStore } from './stores/message';
import { useChatEngine } from './useChatEngine';

const emit = defineEmits<{ 
    (e: 'openLibrary'): void
}>();

const messageStore = useMessageStore();

const { 
    inputText, 
    developerPrompt, 
    send,
    cancel
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