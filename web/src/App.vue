<template>
    <div class="app-layout">
        <!-- Sidebar Component -->
        <Sidebar :isStreaming="isStreaming" />

        <!-- Main Chat Area -->
        <main class="main-area">
            <div class="chat-container">
                <div class="messages-container" ref="messagesContainer">
                    <template v-for="msg in messages" :key="msg.id">
                        <ChatMessage v-if="msg.role !== 'system'" :message="msg" />
                    </template>
                    <div v-if="messages.length === 0" class="empty-state">
                        <h2>Start a new chat</h2>
                    </div>
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
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { useConversations } from './composables/useConversations';
import { useMessages } from './composables/useMessages';
import ChatMessage from './components/ChatMessage.vue';
import Sidebar from './components/Sidebar.vue';

const { currentConversationId, fetchAllConversations, createConversation, selectConversation, generateTitle } = useConversations();
const { messages, activeLeafId, isStreaming, loadConversation, sendMessage, clearMessages, stopStreaming } = useMessages();

const inputText = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// Used to bypass the watcher when transitioning from "new chat" to "chat created"
// to prevent the watcher from fetching the DB and wiping the in-flight user message.
let skipWatch = false;

// On startup, fetch the sidebar list
onMounted(() => {
    fetchAllConversations();
});

// Watch for sidebar selection changes
watch(currentConversationId, (newId) => {
    stopStreaming(); // Kill any active stream before switching
    
    if (skipWatch) {
        skipWatch = false;
        return;
    }
    if (newId) {
        loadConversation(newId);
    } else {
        // If selected conversation is set to null, clear the chat area
        clearMessages();
    }
});

// Watch for new messages to auto-scroll
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
    
    // If currentConversationId is null, we are in the "New Chat" state
    if (!currentConversationId.value) {
        // Create the conversation first
        const result = await createConversation(null, "You are a helpful assistant.");
        if (!result) return;
        
        // Prevent the watcher from firing loadConversation and wiping our pending send
        skipWatch = true; 
        
        // Update states manually
        selectConversation(result.conversationId);
        activeLeafId.value = result.rootMessageId;
        
        // Wait for the user message to be appended
        const userMsgId = await sendMessage(text);
        
        // Auto-generate title in the background (force=false)
        if (userMsgId && currentConversationId.value) {
            generateTitle(currentConversationId.value, false);
        }
    } else {
        await sendMessage(text);
    }
}
</script>

<style scoped>
.app-layout {
    display: flex;
    height: 100vh;
    width: 100%;
}


.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
}

.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 900px;
    margin: 0 auto;
    width: 100%;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
}

.input-container {
    display: flex;
    padding: 15px;
    border-top: 1px solid #ddd;
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

.empty-state {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #888;
}
</style>