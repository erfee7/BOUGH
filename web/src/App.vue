<template>
    <div class="app-layout">
        <Sidebar 
            @openPromptLibrary="isPromptLibraryVisible = true" 
            @navigate="navigate"
        />
        <main class="main-area">
            <GenerationConfigBar />
            <NewChatArea 
                v-if="!conversationStore.currentConversationId" 
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
import { onMounted } from 'vue';
import Sidebar from './chat/sidebar/Sidebar.vue';
import NewChatArea from './chat/NewChatArea.vue';
import ChatArea from './chat/ChatArea.vue';
import PromptLibraryModal from './chat/prompts/PromptLibraryModal.vue';
import GenerationConfigBar from './chat/generation_config/GenerationConfigBar.vue';
import { useConversationStore } from './chat/stores/conversation';
import { useChatEngine } from './chat/useChatEngine';

const conversationStore = useConversationStore();

const { 
    isPromptLibraryVisible,
    initialize, 
    navigate
} = useChatEngine();

onMounted(() => {
    initialize();
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