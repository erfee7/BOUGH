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
import Sidebar from './sidebar/Sidebar.vue';
import NewChatArea from './NewChatArea.vue';
import ChatArea from './ChatArea.vue';
import PromptLibraryModal from './prompts/PromptLibraryModal.vue';
import GenerationConfigBar from './generation_config/GenerationConfigBar.vue';
import { useConversationStore } from './stores/conversation';
import { useChatEngine } from './useChatEngine';

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