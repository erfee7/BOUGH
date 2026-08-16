<template>
    <div class="chat-container">
        <MessageList />
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
            @openLibrary="emit('openLibrary')"
            :isStreaming="messageStore.isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue';
import InputArea from './InputArea.vue';
import { useMessageStore } from './stores/message';
import { useChatEngine } from './useChatEngine';
import { useAttachmentStore } from './stores/attachment';

const attachmentStore = useAttachmentStore();

const emit = defineEmits<{ 
    (e: 'openLibrary'): void
}>();

const messageStore = useMessageStore();

const { 
    inputText, 
    developerPrompt, 
    send,
    cancel
} = useChatEngine();
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    flex: 1; /* Take remaining space instead of 100% */
    min-height: 0; /* Allow shrinking for internal scroll */
    width: 100%;
    margin: 0 auto;
}
</style>