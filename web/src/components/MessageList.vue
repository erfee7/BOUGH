<template>
    <div class="messages-container" ref="messagesContainer">
        <template v-for="msg in messages" :key="msg.id">
            <ChatMessage v-if="msg.role !== 'system' && msg.role !== 'developer'" :message="msg" />
        </template>
        <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">💬</div>
            <h2>Start a new chat</h2>
            <p>Type a message below to begin</p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { Message } from '../types';
import ChatMessage from './ChatMessage.vue';

const props = defineProps<{ messages: Message[] }>();

const messagesContainer = ref<HTMLElement | null>(null);

watch(() => props.messages, async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
}, { deep: true });
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