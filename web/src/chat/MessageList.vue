<template>
    <div class="messages-container" ref="messagesContainer">
        <template v-for="msg in activePath" :key="msg.id">
            <ChatMessage 
                v-if="msg.role !== 'system' && msg.role !== 'developer'" 
                :message="msg" 
                :siblingInfo="getSiblingInfoUtil(msg.id, messages)"
                :isStreaming="isStreaming"
                :isEditing="editingMessageId === msg.id"
                :editingText="editingText"
                @update:editingText="editingText = $event"
                @switch-sibling="(direction: 'prev' | 'next') => switchSibling(msg.id, direction)"
                @generate="generateMessage(msg.id)"
                @start-edit="startEdit(msg)"
                @cancel-edit="cancelEdit()"
                @save-edit="(shouldGenerate: boolean) => saveEdit(msg, shouldGenerate)"
            />
        </template>
        <div v-if="activePath.length === 0" class="empty-state">
            <div class="empty-icon">💬</div>
            <h2>Start a new chat</h2>
            <p>Type a message below to begin</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import ChatMessage from './message/ChatMessage.vue';
import { useBranching } from './useBranching';
import { useMessages } from './useMessages.js';
import { getSiblingInfo as getSiblingInfoUtil } from './branchingUtils.js';

const { messages } = useMessages();
const { 
    activePath, 
    isStreaming, 
    editingMessageId, 
    editingText, 
    switchSibling, 
    startEdit, 
    cancelEdit, 
    saveEdit, 
    generateMessage 
} = useBranching();
</script>

<style scoped>
.messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px 2%; /* Wider responsive padding */
    scrollbar-width: thin;
    scrollbar-color: #334155 transparent;
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
    background-color: #334155;
    border-radius: 3px;
}

.empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #64748b;
    margin-top: 10vh;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 8px 0;
}

.empty-state p {
    font-size: 14px;
    margin: 0;
}
</style>