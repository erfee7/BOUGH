<template>
    <div class="messages-container" ref="messagesContainer">
        <template v-for="msg in activePath" :key="msg.id">
            <ChatMessage 
                v-if="msg.role !== 'system' && msg.role !== 'developer'" 
                :message="msg" 
                :allMessages="allMessages"
                :isStreaming="isStreaming"
                :isEditing="editingMessageId === msg.id"
                :editingText="editingText"
                @update:editingText="(val: string) => emit('update:editingText', val)"
                @switch-sibling="(direction: 'prev' | 'next') => emit('switch-sibling', msg.id, direction)"
                @generate="emit('generate', msg.id)"
                @start-edit="emit('start-edit', msg)"
                @cancel-edit="emit('cancel-edit')"
                @save-edit="(shouldGenerate: boolean) => emit('save-edit', msg, shouldGenerate)"
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
import ChatMessage from './ChatMessage.vue';
import { Message } from '../types';

defineProps<{ 
    activePath: Message[], 
    allMessages: Message[],
    isStreaming: boolean,
    editingMessageId: string | null,
    editingText: string
}>();

const emit = defineEmits<{
    (e: 'switch-sibling', messageId: string, direction: 'prev' | 'next'): void,
    (e: 'generate', messageId: string): void,
    (e: 'start-edit', message: Message): void,
    (e: 'cancel-edit'): void,
    (e: 'save-edit', message: Message, shouldGenerate: boolean): void,
    (e: 'update:editingText', value: string): void
}>();
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