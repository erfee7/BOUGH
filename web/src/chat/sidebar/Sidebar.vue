<template>
    <aside class="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-btn" @click="handleNewChat" :disabled="props.isStreaming">
                <span>+</span> New Chat
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
                        <button 
                            v-if="!isGenerating(conv.id)"
                            @click.stop="handleGenerateTitle(conv.id)" 
                            class="title-action-btn"
                            title="Generate Title"
                        >✨</button>
                        <span v-else class="spinner">⏳</span>
                    </div>
                </li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <button class="library-btn" @click="emit('openPromptLibrary')">
                ⚙️ Prompt Library
            </button>
        </div>
    </aside>
</template>

<script setup lang="ts">
import { useConversations } from '../useConversations';
import { useTitleEdit } from './useTitleEdit';

const props = defineProps<{ isStreaming: boolean }>();
const emit = defineEmits<{ (e: 'openPromptLibrary'): void }>(); // Add emit

const { conversations, currentConversationId, selectConversation, generatingTitleIds, generateTitle } = useConversations();
const { editingId, editText, startEditing, saveEdit, cancelEdit } = useTitleEdit();

// Custom directive to auto-focus and select text when the input is mounted
const vFocus = {
    mounted: (el: HTMLInputElement) => {
        el.focus();
        el.select();
    }
};

function handleNewChat() {
    if (props.isStreaming) return;
    selectConversation(null);
}

function isGenerating(id: string) {
    return generatingTitleIds.value.includes(id);
}

function handleGenerateTitle(id: string) {
    generateTitle(id, true);
}
</script>

<style scoped>
.sidebar {
    width: 280px;
    background: #0b0f19;
    border-right: 1px solid #1e293b;
    display: flex;
    flex-direction: column;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #1e293b;
}

.new-chat-btn {
    width: 100%;
    padding: 10px;
    background: transparent;
    color: #f8fafc;
    border: 1px dashed #334155;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s;
}

.new-chat-btn span {
    font-size: 18px;
    line-height: 1;
}

.new-chat-btn:hover:not(:disabled) {
    background: #1e293b;
    border-color: #475569;
}

.new-chat-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.conversation-list-container {
    flex: 1;
    overflow-y: auto;
    padding: 12px 8px;
    scrollbar-width: thin;
    scrollbar-color: #334155 transparent;
}

.conversation-list-container::-webkit-scrollbar {
    width: 6px;
}

.conversation-list-container::-webkit-scrollbar-thumb {
    background-color: #334155;
    border-radius: 3px;
}

.conversation-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.conversation-list li {
    padding: 10px 12px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #cbd5e1;
    transition: background-color 0.15s, color 0.15s;
}

.conversation-list li:hover {
    background: #1e293b;
    color: #f8fafc;
}

.conversation-list li.active {
    background: #1e293b;
    color: #f8fafc;
    font-weight: 500;
}

.conv-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

.conv-title {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.edit-input {
    width: 100%;
    background: #0f172a;
    color: #f8fafc;
    border: 1px solid #3b82f6;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    padding: 4px 8px;
    outline: none;
    box-sizing: border-box;
}

.title-action-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    opacity: 0;
    transition: opacity 0.15s, transform 0.15s;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

li:hover .title-action-btn {
    opacity: 1;
}

.title-action-btn:hover {
    transform: scale(1.15);
}

.spinner {
    font-size: 14px;
    opacity: 1;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.sidebar-footer {
    padding: 16px;
    border-top: 1px solid #1e293b;
}

.library-btn {
    width: 100%;
    padding: 10px;
    background: transparent;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s;
}

.library-btn:hover {
    background: #1e293b;
    color: #f8fafc;
    border-color: #475569;
}
</style>