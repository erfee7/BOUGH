<template>
    <div class="app-layout">
        <Sidebar 
            :class="{ open: isSidebarOpen }"
            @openPromptLibrary="openPromptLibrary" 
            @navigate="onNavigate"
            @openSettings="openSettings"
        />
        <div v-if="isSidebarOpen" class="sidebar-backdrop" @click="isSidebarOpen = false"></div>
        <main class="main-area">
            <GenerationConfigBar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />
            <div class="content-region">
                <NewChatArea
                    v-if="!conversationStore.currentConversationId"
                    :systemPrompt="systemPrompt"
                    @update:systemPrompt="systemPrompt = $event"
                    @openLibrary="isPromptLibraryVisible = true"
                />
                <MessageList v-else />
                <InputArea 
                    :modelValue="inputText" 
                    @update:modelValue="inputText = $event"
                    :developerPrompt="developerPrompt"
                    @update:developerPrompt="developerPrompt = $event"
                    :drafts="attachmentStore.drafts"
                    @files-added="attachmentStore.addFiles"
                    @remove-draft="attachmentStore.removeDraft"
                    @retry-draft="attachmentStore.retryDraft"
                    @send="send"
                    @cancel="cancel"
                    @openLibrary="isPromptLibraryVisible = true"
                    :isStreaming="messageStore.isStreaming"
                />
            </div>
        </main>
        <PromptLibraryModal 
            :isVisible="isPromptLibraryVisible" 
            @close="isPromptLibraryVisible = false" 
        />
        <SettingsModal 
            v-if="isSettingsVisible && authStore.user" 
            :username="authStore.user.username" 
            @close="isSettingsVisible = false" 
            @logout="handleLogout"
        />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Sidebar from './sidebar/Sidebar.vue';
import NewChatArea from './NewChatArea.vue';
import MessageList from './MessageList.vue';
import InputArea from './InputArea.vue';
import PromptLibraryModal from './prompts/PromptLibraryModal.vue';
import GenerationConfigBar from './generation_config/GenerationConfigBar.vue';
import SettingsModal from '@/shared/SettingsModal.vue';
import { useConversationStore } from './stores/conversation';
import { useMessageStore } from './stores/message';
import { useAttachmentStore } from './stores/attachment';
import { useChatEngine } from './useChatEngine';
import { useAuthStore } from '@/auth/stores/auth';

const conversationStore = useConversationStore();
const messageStore = useMessageStore();
const attachmentStore = useAttachmentStore();
const authStore = useAuthStore();

// The single engine instance: the composer is shell-level chrome, so its
// orchestrator lives here — never unmounted, shared by every view.
const { 
    isPromptLibraryVisible,
    inputText,
    systemPrompt,
    developerPrompt,
    initialize, 
    navigate,
    send,
    cancel
} = useChatEngine();

const isSettingsVisible = ref(false);

const isSidebarOpen = ref(false);

function onNavigate(id: string | null) {
    isSidebarOpen.value = false; // Auto-close the drawer after any navigation
    navigate(id);
}

function openSettings() {
    isSidebarOpen.value = false;
    isSettingsVisible.value = true;
}

function openPromptLibrary() {
    isSidebarOpen.value = false;
    isPromptLibraryVisible.value = true;
}

function handleLogout() {
    isSettingsVisible.value = false;
    authStore.logout();
}

onMounted(() => {
    initialize();
});
</script>

<style scoped>
.app-layout {
    display: flex;
    height: 100vh;
    height: 100dvh;
    width: 100%;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-area {
    flex: 1;
    min-width: 0; /* Allow shrinking below the config bar's intrinsic width — kills the ~740px page floor */
    display: flex;
    flex-direction: column;
    position: relative;
}

.content-region {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-end; /* Composer alone in flow (welcome case) -> pinned to bottom */
    position: relative;        /* Reference frame for the welcome overlay */
}

.sidebar-backdrop {
    display: none;
}

@media (max-width: 768px) {
    .sidebar-backdrop {
        display: block;
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 800;
    }
}
</style>