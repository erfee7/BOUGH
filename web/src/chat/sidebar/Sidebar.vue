<template>
    <aside class="sidebar">
        <div class="sidebar-header">
            <button class="btn-secondary new-chat-btn" @click="handleNewChat">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.square_pen"></svg>
                New Chat
            </button>
        </div>
        <div class="conversation-list-container">
            <ul class="conversation-list">
                <li 
                    v-for="conv in conversationStore.conversations" 
                    :key="conv.id" 
                    @click="handleSelect(conv.id)"
                    @dblclick="startEditing(conv)"
                    :class="{ 'active': conv.id === conversationStore.currentConversationId }"
                >
                    <input 
                        v-if="editingId === conv.id"
                        v-model="editText"
                        v-focus
                        @keydown.enter.exact.prevent="saveEdit"
                        @keydown.esc.exact="cancelEdit"
                        @blur="saveEdit"
                        class="edit-input"
                    />
                    <div v-else class="conv-item-content">
                        <span class="conv-title">{{ conv.title || 'Untitled' }}</span>
                        
                        <ConversationMenu 
                            :isGenerating="isGenerating(conv.id)"
                            @rename="startEditing(conv)"
                            @generate-title="handleGenerateTitle(conv.id)"
                            @touch="handleTouch(conv.id)"
                            @delete="handleDelete(conv.id)"
                        />
                    </div>
                </li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <button class="btn-ghost library-btn" @click="emit('openPromptLibrary')">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.book_open"></svg>
                Prompt Library
            </button>
            
            <button class="btn-ghost settings-btn" @click="emit('openSettings')">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.settings"></svg>
                Settings
            </button>
        </div>
    </aside>
</template>

<script setup lang="ts">
import { useConversationStore } from '@/chat/stores/conversation';
import { useTitleEdit } from './useTitleEdit';
import ConversationMenu from './ConversationMenu.vue';
import { ICONS } from '@/icons';

const emit = defineEmits<{ 
    (e: 'openPromptLibrary'): void,
    (e: 'navigate', id: string | null): void,
    (e: 'openSettings'): void
}>();

const conversationStore = useConversationStore();
const { editingId, editText, startEditing, saveEdit, cancelEdit } = useTitleEdit();

// Custom directive to auto-focus and select text when the input is mounted
const vFocus = {
    mounted: (el: HTMLInputElement) => {
        el.focus();
        el.select();
    }
};

function isGenerating(id: string) {
    return conversationStore.generatingTitleIds.includes(id);
}

function handleGenerateTitle(id: string) {
    conversationStore.generateTitle(id, true);
}

function handleTouch(id: string) {
    conversationStore.touchConversation(id);
}

function handleNewChat() {
    emit('navigate', null);
}

function handleSelect(id: string) {
    emit('navigate', id);
}

async function handleDelete(id: string) {
    const wasActive = conversationStore.currentConversationId === id;
    await conversationStore.deleteConversation(id);
    // If we deleted the active conversation, explicitly navigate to New Chat state
    if (wasActive) {
        emit('navigate', null);
    }
}
</script>

<style scoped>
.sidebar {
    width: 280px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-default);
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-default);
}

.new-chat-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.conversation-list-container {
    flex: 1;
    overflow-y: auto;
    padding: 12px 8px;
}

.conversation-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.conversation-list li {
    padding: 10px 12px;
    margin-bottom: 4px;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: 14px;
    color: var(--text-secondary);
    transition: background-color 0.15s, color 0.15s;
}

.conversation-list li:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.conversation-list li.active {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-weight: 500;
}

.conv-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    min-height: 26px; /* Prevents layout shift when menu/spinner toggles */
}

.conv-title {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.edit-input {
    width: 100%;
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--accent-blue);
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-family: inherit;
    padding: 4px 8px;
    outline: none;
    box-sizing: border-box;
}

/* Reveal kebab menu on row hover */
.conversation-list li:hover :deep(.kebab-btn) {
    opacity: 1;
}

.sidebar-footer {
    padding: 16px;
    border-top: 1px solid var(--border-default);
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.library-btn, .settings-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.settings-btn {
    border-top: 1px solid var(--border-default);
    padding-top: 16px;
    margin-top: 8px;
}

.settings-container {
    border-top: 1px solid var(--border-default);
    padding-top: 8px;
    margin-top: 8px;
}

/* Touch devices: kebab is never hover-revealed */
@media (hover: none) {
    .conversation-list li :deep(.kebab-btn) {
        opacity: 1;
    }
}

/* Mobile: overlay drawer, hidden off-canvas until .open */
@media (max-width: 768px) {
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        bottom: 0;
        z-index: 900;
        transform: translateX(-100%);
        transition: transform 0.2s ease;
    }
    .sidebar.open {
        transform: translateX(0);
    }
}
</style>