<template>
    <div class="app-layout">
        <!-- Sidebar -->
        <aside class="sidebar">
            <button class="new-chat-btn" @click="handleNewChat" :disabled="isStreaming">
                + New Chat
            </button>
            <ul class="conversation-list">
                <li 
                    v-for="conv in conversations" 
                    :key="conv.id" 
                    @click="selectConversation(conv.id)"
                    :class="{ 'active': conv.id === currentConversationId }"
                >
                    {{ conv.title || 'Untitled' }}
                </li>
            </ul>
        </aside>

        <!-- Main Chat Area -->
        <main class="main-area">
            <div v-if="currentConversationId" class="chat-container">
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
            <div v-else class="empty-state">
                <h2>Select or create a chat</h2>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { useConversations } from './composables/useConversations';
import { useMessages } from './composables/useMessages';
import ChatMessage from './components/ChatMessage.vue';

const { conversations, currentConversationId, fetchAllConversations, createConversation, selectConversation } = useConversations();
const { messages, isStreaming, loadConversation, sendMessage } = useMessages();

const inputText = ref('');
const messagesContainer = ref<HTMLElement | null>(null);

// On startup, fetch the sidebar list
onMounted(() => {
    fetchAllConversations();
});

// Watch for sidebar selection changes
watch(currentConversationId, (newId) => {
    if (newId) {
        loadConversation(newId);
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
    await sendMessage(text);
}

async function handleNewChat() {
    if (isStreaming.value) return;
    await createConversation();
}
</script>

<style scoped>
.app-layout {
    display: flex;
    height: 100vh;
    width: 100%;
}

.sidebar {
    width: 260px;
    background: #f7f7f8;
    border-right: 1px solid #ddd;
    display: flex;
    flex-direction: column;
}

.new-chat-btn {
    margin: 15px;
    padding: 10px;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
}

.new-chat-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.conversation-list {
    list-style: none;
    padding: 0;
    margin: 0;
    overflow-y: auto;
    flex: 1;
}

.conversation-list li {
    padding: 12px 15px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.conversation-list li:hover {
    background: #ececf1;
}

.conversation-list li.active {
    background: #dcdce5;
    font-weight: bold;
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