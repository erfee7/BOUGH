<template>
    <div class="app-layout">
        <Sidebar 
            @openPromptLibrary="isPromptLibraryVisible = true" 
            @navigate="navigate"
            @openSettings="isSettingsVisible = true"
        />
        <main class="main-area">
            <GenerationConfigBar />
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

.content-region {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    justify-content: flex-end; /* Composer alone in flow (welcome case) -> pinned to bottom */
    position: relative;        /* Reference frame for the welcome overlay */
}
</style>