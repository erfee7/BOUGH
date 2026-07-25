<template>
    <div class="app-layout">
        <Sidebar :isStreaming="isStreaming" />
        <main class="main-area">
            <NewChatArea 
                v-if="!currentConversationId" 
                :modelValue="inputText" 
                @update:modelValue="inputText = $event"
                @send="send"
                :isStreaming="isStreaming"
            />
            <ChatArea 
                v-else 
                :messages="messages" 
                :modelValue="inputText" 
                @update:modelValue="inputText = $event"
                @send="send"
                :isStreaming="isStreaming"
            />
        </main>
    </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import Sidebar from './components/Sidebar.vue';
import NewChatArea from './components/NewChatArea.vue';
import ChatArea from './components/ChatArea.vue';
import { useChatEngine } from './composables/useChatEngine';

const { 
    currentConversationId, 
    messages, 
    isStreaming, 
    inputText, 
    initialize, 
    handleNavigation, 
    send 
} = useChatEngine();

onMounted(() => {
    initialize();
});

watch(currentConversationId, (newId) => {
    handleNavigation(newId);
});
</script>

<style scoped>
.app-layout {
    display: flex;
    height: 100vh;
    width: 100%;
    background: #0f172a;
    color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
}
</style>

<style>
/* Global styles to strip browser defaults */
html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    background-color: #0f172a; /* Matches our dark theme */
    overflow: hidden; /* Prevents the "shaking" bounce effect */
}
</style>