<template>
    <div class="chat-container">
        <div class="header">
            <h1>BOUGH Chat</h1>
            <button @click="handleNewChat" :disabled="isStreaming">New Chat</button>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
            <template v-for="msg in messages" :key="msg.id">
                <ChatMessage v-if="msg.role !== 'system'" :message="msg" />
            </template>
        </div>
        
        <div class="input-container">
            <textarea 
                v-model="inputText" 
                @keydown.enter.exact.prevent="handleSend"
                placeholder="Type a message... (Enter to send)"
                :disabled="isStreaming"
            ></textarea>
            <button @click="handleSend" :disabled="isStreaming || !inputText.trim()">
                Send
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useChat } from './composables/useChat';
import ChatMessage from './components/ChatMessage.vue';

const { messages, isStreaming, sendMessage, createConversation } = useChat();
const inputText = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// Auto-scroll to bottom when messages array changes or content updates
watch(messages, async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
}, { deep: true });

async function handleSend() {
    if (!inputText.value.trim() || isStreaming.value) return;
    const text = inputText.value;
    inputText.value = '';
    await sendMessage(text);
}

async function handleNewChat() {
    if (isStreaming.value) return;
    await createConversation();
}
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    border-left: 1px solid #ddd;
    border-right: 1px solid #ddd;
}

.header {
    padding: 10px 20px;
    background: #fff;
    border-bottom: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    margin: 0;
    font-size: 1.2rem;
    color: #333;
}

.header button {
    padding: 8px 16px;
    cursor: pointer;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: bold;
}

.header button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #fafafa;
}

.input-container {
    display: flex;
    padding: 15px;
    border-top: 1px solid #ddd;
    background: #fff;
}

.input-container textarea {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: none;
    height: 50px;
    font-family: inherit;
    font-size: 14px;
}

.input-container button {
    margin-left: 10px;
    padding: 0 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.input-container button:disabled {
    background: #ccc;
    cursor: not-allowed;
}
</style>