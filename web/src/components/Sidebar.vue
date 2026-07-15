<template>
    <aside class="sidebar">
        <button class="new-chat-btn" @click="handleNewChat" :disabled="isStreaming">
            + New Chat
        </button>
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
                    @keydown.enter.exact.prevent="saveEdit"
                    @keydown.esc.exact="cancelEdit"
                    @blur="saveEdit"
                    ref="editInput"
                    class="edit-input"
                />
                <span v-else>{{ conv.title || 'Untitled' }}</span>
            </li>
        </ul>
    </aside>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import { useConversations } from '../composables/useConversations';
import { ConversationSummary } from '../types';

// Assign defineProps to a variable to access it in the script
const props = defineProps<{ isStreaming: boolean }>();

const { conversations, currentConversationId, selectConversation, updateTitle } = useConversations();

const editingId = ref<string | null>(null);
const editText = ref<string>('');
const editInput = ref<HTMLInputElement | null>(null);

async function startEditing(conv: ConversationSummary) {
    editingId.value = conv.id;
    editText.value = conv.title || '';
    await nextTick();
    if (editInput.value) {
        editInput.value.focus();
        editInput.value.select();
    }
}

function saveEdit() {
    if (editingId.value) {
        // Only save if changed
        const conv = conversations.value.find(c => c.id === editingId.value);
        if (conv && (conv.title || '') !== editText.value.trim()) {
            updateTitle(editingId.value, editText.value);
        }
        editingId.value = null;
    }
}

function cancelEdit() {
    editingId.value = null;
    editText.value = '';
}

function handleNewChat() {
    if (props.isStreaming) return;
    selectConversation(null);
}
</script>

<style scoped>
.sidebar {
    width: 260px;
    background: #f7f7f8;
    border-right: 1px solid #ddd;
    display: flex;
    flex-direction: column;
}

.new-chat-btn {
    margin: 15px;
    padding: 10px;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
}

.new-chat-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.conversation-list {
    list-style: none;
    padding: 0;
    margin: 0;
    overflow-y: auto;
    flex: 1;
}

.conversation-list li {
    padding: 12px 15px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.conversation-list li:hover {
    background: #ececf1;
}

.conversation-list li.active {
    background: #dcdce5;
    font-weight: bold;
}

.edit-input {
    width: 100%;
    padding: 2px 4px;
    margin: -2px -4px;
    border: 1px solid #007bff;
    border-radius: 4px;
    font-size: 14px;
    font-family: inherit;
    /* Prevent text from breaking out of the li container */
    box-sizing: border-box;
}
</style>