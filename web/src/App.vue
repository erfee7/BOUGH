<template>
    <div class="app-layout">
        <Sidebar 
            :isStreaming="isStreaming" 
            @openPromptLibrary="isPromptLibraryVisible = true" 
        />
        <main class="main-area">
            <NewChatArea 
                v-if="!currentConversationId" 
                @openLibrary="isPromptLibraryVisible = true"
            />
            <ChatArea 
                v-else 
                @openLibrary="isPromptLibraryVisible = true"
            />
        </main>
        <PromptLibraryModal 
            :isVisible="isPromptLibraryVisible" 
            @close="isPromptLibraryVisible = false" 
        />
    </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue';
import Sidebar from './chat/sidebar/Sidebar.vue';
import NewChatArea from './chat/NewChatArea.vue';
import ChatArea from './chat/ChatArea.vue';
import PromptLibraryModal from './chat/prompts/PromptLibraryModal.vue';
import { useMessages } from './chat/useMessages';
import { useConversations } from './chat/useConversations';
import { useChatEngine } from './chat/useChatEngine';

const {
    isStreaming
} = useMessages();

const {
    currentConversationId
} = useConversations();

const { 
    isPromptLibraryVisible,
    initialize, 
    handleNavigation
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
    background-color: #0f172a;
    overflow: hidden;
}
</style>