<template>
    <div class="messages-container" ref="messagesContainer">
        <ChatMessage 
            v-for="msg in activePath" 
            :key="msg.id"
            :message="msg" 
            :siblingInfo="getSiblingInfoUtil(msg.id, messageStore.messages)"
            :isEditing="editingMessageId === msg.id"
            :editingText="editingText"
            @update:editingText="editingText = $event"
            @switch-sibling="(direction: 'prev' | 'next') => switchSibling(msg.id, direction)"
            @generate="messageStore.generateMessage(msg.id)"
            @start-edit="startEdit(msg)"
            @cancel-edit="cancelEdit()"
            @save-edit="(shouldGenerate: boolean) => saveEdit(msg, shouldGenerate)"
        />
    </div>
</template>

<script setup lang="ts">
import ChatMessage from './message/ChatMessage.vue';
import { useBranching } from './useBranching';
import { useMessageStore } from './stores/message';
import { getSiblingInfo as getSiblingInfoUtil } from './branchingUtils.js';

const messageStore = useMessageStore();

const { 
    activePath, 
    editingMessageId, 
    editingText, 
    switchSibling, 
    startEdit, 
    cancelEdit, 
    saveEdit
} = useBranching();
</script>

<style scoped>
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px 2%; /* Wider responsive padding */
    scrollbar-width: thin;
    scrollbar-color: var(--bg-tertiary) transparent;
}

@media (max-width: 1024px) {
    .messages-container {
        padding: 24px 16px; /* Tighter on small screens */
    }
}

.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-thumb {
    background-color: var(--bg-tertiary);
    border-radius: 3px;
}
</style>