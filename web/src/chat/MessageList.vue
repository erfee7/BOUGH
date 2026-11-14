<template>
    <div class="messages-container" ref="messagesContainer">
        <div ref="messagesContent">
            <ChatMessage 
                v-for="msg in messageStore.activePath" 
                :key="msg.id"
                :data-message-id="msg.id"
                :message="msg" 
                :siblingInfo="getSiblingInfoUtil(msg.id, messageStore.messages)"
                :isEditing="editingMessageId === msg.id"
                :editingText="editingText"
                @update:editingText="editingText = $event"
                @switch-sibling="(direction: 'prev' | 'next') => handleSwitchSibling(msg, direction)"
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
import { ref, watch, onUnmounted, nextTick } from 'vue';
import ChatMessage from './message/ChatMessage.vue';
import { useMessageStore } from './stores/message';
import { useMessageEdit } from './useMessageEdit';
import { useGenerationConfigStore } from './stores/generationConfig';
import { usePresetStore } from './stores/preset';
import { useMessageScroll } from './useMessageScroll';
import { getSiblingInfo as getSiblingInfoUtil } from './branchingUtils.js';
import type { Message } from '@/types';

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
    scrollNextMessage,
    scrollMessageIntoView
} = useMessageScroll(messagesContainer, messagesContent);

watch([canScrollUp, canScrollDown], ([up, down]) => {
    emit('scroll-state', { canScrollUp: up, canScrollDown: down });
}, { immediate: true });

onUnmounted(() => {
    emit('scroll-state', { canScrollUp: false, canScrollDown: false });
});

// --- Auto-scroll ---

// Appends during this conversation: SAME array reference (pushed, not
// replaced) + grown length -> glide to the new tail. Covers send, generate,
// fork-save and Save & Send. Array replacement (conversation load/reload)
// and branch switches (no growth) are excluded by construction: fresh mounts
// start at the top, and sibling switches anchor separately below.

// Judge whether the active leaf changing is due to an append
let prevMessages: Message[] = messageStore.messages;
let prevLength = messageStore.messages.length;

watch(() => messageStore.activeLeafId, (newLeafId) => {
    const appended =
        prevMessages === messageStore.messages &&
        messageStore.messages.length > prevLength;
    prevMessages = messageStore.messages;
    prevLength = messageStore.messages.length;

    if (!newLeafId || !appended) return;
    nextTick(() => scrollToBottom());
});

// Wait for EditArea before scrolling to it
watch(editingMessageId, async (id) => {
    if (!id) return;
    await nextTick();
    scrollMessageIntoView(id);
});

// Branch switch: pin the switched message's footer at the same screen position
async function handleSwitchSibling(msg: Message, direction: 'prev' | 'next') {
    const container = messagesContainer.value;
    if (!container) {
        messageStore.switchSibling(msg.id, direction);
        return;
    }

    const index = messageStore.activePath.findIndex(m => m.id === msg.id);
    const containerTop = container.getBoundingClientRect().top;
    const tile = container.querySelector<HTMLElement>(`[data-message-id="${msg.id}"]`);
    const relOld = tile ? tile.getBoundingClientRect().bottom - containerTop : null;

    messageStore.switchSibling(msg.id, direction);

    if (relOld === null || index === -1) return;
    await nextTick();

    const newMsg = messageStore.activePath[index];
    const newTile = newMsg
        ? container.querySelector<HTMLElement>(`[data-message-id="${newMsg.id}"]`)
        : null;
    if (!newTile) return;

    // Scroll clamped, so the new footer always ends up on-screen even for short siblings near the edges
    const newBottom =
        newTile.getBoundingClientRect().bottom - containerTop + container.scrollTop;
    const target = newBottom - relOld;
    const maxScrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
    container.scrollTop = Math.min(Math.max(target, 0), maxScrollTop);
}

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