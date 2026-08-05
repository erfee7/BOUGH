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
                    v-for="conv in conversations" 
                    :key="conv.id" 
                    @click="selectConversation(conv.id)"
                    @dblclick="startEditing(conv)"
                    :class="{ 'active': conv.id === currentConversationId }"
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
                            @delete="deleteConversation(conv.id)"
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
        </div>
    </aside>
</template>

<script setup lang="ts">
import { useConversations } from '@/chat/useConversations';
import { useTitleEdit } from './useTitleEdit';
import ConversationMenu from './ConversationMenu.vue';
import { ICONS } from '@/icons';

const emit = defineEmits<{ (e: 'openPromptLibrary'): void }>();

const { conversations, currentConversationId, selectConversation, generatingTitleIds, generateTitle, touchConversation, deleteConversation } = useConversations();
const { editingId, editText, startEditing, saveEdit, cancelEdit } = useTitleEdit();

// Custom directive to auto-focus and select text when the input is mounted
const vFocus = {
    mounted: (el: HTMLInputElement) => {
        el.focus();
        el.select();
    }
};

function handleNewChat() {
    selectConversation(null);
}

function isGenerating(id: string) {
    return generatingTitleIds.value.includes(id);
}

function handleGenerateTitle(id: string) {
    generateTitle(id, true);
}

function handleTouch(id: string) {
    touchConversation(id);
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
}

.library-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
</style>