<template>
    <div class="app-layout">
        <Sidebar 
            @openPromptLibrary="isPromptLibraryVisible = true" 
        />
        <main class="main-area">
            <GenerationConfigBar />
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
import GenerationConfigBar from './chat/generation_config/GenerationConfigBar.vue';
import { useMessages } from './chat/useMessages';
import { useConversations } from './chat/useConversations';
import { useChatEngine } from './chat/useChatEngine';

const {
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
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
}
</style>