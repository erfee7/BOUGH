<template>
    <div class="messages-container" ref="messagesContainer">
        <div ref="messagesContent">
            <ChatMessage 
                v-for="msg in messageStore.activePath" 
                :key="msg.id"
                :message="msg" 
                :siblingInfo="getSiblingInfoUtil(msg.id, messageStore.messages)"
                :isEditing="editingMessageId === msg.id"
                :editingText="editingText"
                @update:editingText="editingText = $event"
                @switch-sibling="(direction: 'prev' | 'next') => messageStore.switchSibling(msg.id, direction)"
                @generate="messageStore.generateMessage(msg.id)"
                @start-edit="startEdit(msg)"
                @cancel-edit="cancelEdit()"
                @save-edit="(shouldGenerate: boolean) => saveEdit(msg, shouldGenerate)"
                @load-config="generationConfigStore.loadFromCreationData(msg.creation_data, presetStore.presets)"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import ChatMessage from './message/ChatMessage.vue';
import { useMessageStore } from './stores/message';
import { useMessageEdit } from './useMessageEdit';
import { useGenerationConfigStore } from './stores/generationConfig';
import { usePresetStore } from './stores/preset';
import { useMessageScroll } from './useMessageScroll';
import { getSiblingInfo as getSiblingInfoUtil } from './branchingUtils.js';

const messageStore = useMessageStore();
const generationConfigStore = useGenerationConfigStore();
const presetStore = usePresetStore();

const { 
    editingMessageId, 
    editingText, 
    startEdit, 
    cancelEdit, 
    saveEdit
} = useMessageEdit();

const emit = defineEmits<{
    (e: 'scroll-state', state: { canScrollUp: boolean; canScrollDown: boolean }): void
}>();

const messagesContainer = ref<HTMLElement | null>(null);
const messagesContent = ref<HTMLElement | null>(null);

const {
    canScrollUp,
    canScrollDown,
    scrollToTop,
    scrollToBottom,
    scrollPrevMessage,
    scrollNextMessage
} = useMessageScroll(messagesContainer, messagesContent);

watch([canScrollUp, canScrollDown], ([up, down]) => {
    emit('scroll-state', { canScrollUp: up, canScrollDown: down });
}, { immediate: true });

onUnmounted(() => {
    emit('scroll-state', { canScrollUp: false, canScrollDown: false });
});

defineExpose({
    scrollToTop,
    scrollToBottom,
    scrollPrevMessage,
    scrollNextMessage
});
</script>

<style scoped>
.messages-container {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 0 2% 24px;
    scrollbar-width: thin;
    scrollbar-color: var(--bg-tertiary) transparent;
}

.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-thumb {
    background-color: var(--bg-tertiary);
    border-radius: 3px;
}
</style>