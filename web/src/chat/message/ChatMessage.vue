<template>
    <div class="message-tile" :class="{ 'user-role': message.role === 'user', 'assistant-role': message.role === 'assistant', 'error': message.status === 'error' }">
        <div class="avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.user"></svg>
            <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.bot"></svg>
        </div>
        <div class="message-body">
            <div class="message-header">
                <span class="role-label">{{ message.role === 'user' ? 'User' : 'Assistant' }}</span>
                <span class="msg-time" :title="formatAbsoluteTime(message.created_at)">{{ formatRelativeTime(message.created_at) }}</span>
            </div>
            
            <!-- Edit Mode -->
            <EditArea 
                v-if="isEditing"
                :editingText="editingText"
                :role="message.role"
                @update:editingText="emit('update:editingText', $event)"
                @save-edit="emit('save-edit', $event)"
                @cancel-edit="emit('cancel-edit')"
            />

            <!-- Normal Mode -->
            <template v-else>
                <ReasoningBlock 
                    v-if="message.reasoning" 
                    :reasoning="message.reasoning" 
                    :status="message.status" 
                    :content="message.content"
                />

                <div class="message-content">
                    <MdPreview 
                        v-if="message.content"
                        :modelValue="message.content" 
                        theme="dark" 
                        :previewTheme="'github'" 
                        :codeTheme="'github'" 
                        :language="'en-US'"
                        :class="`markdown-content ${message.status === 'streaming' && message.content ? 'streaming' : ''}`"
                        @dblclick="handleMarkdownDblClick"
                        @copy="handleMarkdownCopy"
                    />
                    <span v-else-if="message.status === 'pending' || message.status === 'streaming'" class="placeholder">Thinking...</span>
                    <span v-else>Empty</span>
                </div>

                <MessageActions 
                    :siblingInfo="siblingInfo" 
                    :isInteractive="message.status === 'complete' || message.status === 'canceled'"
                    :role="message.role"
                    :content="message.content"
                    @switch-sibling="emit('switch-sibling', $event)"
                    @start-edit="emit('start-edit')"
                    @generate="emit('generate')"
                />
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import { Message } from '@/types';
import EditArea from './EditArea.vue';
import ReasoningBlock from './ReasoningBlock.vue';
import MessageActions from './MessageActions.vue';
import { ICONS } from '@/icons';
import { handleMarkdownDblClick, handleMarkdownCopy } from '@/chat/markdownInteractions';
import { formatRelativeTime, formatAbsoluteTime } from '@/utils/time';

defineProps<{ 
    message: Message,
    siblingInfo: { count: number, currentIndex: number },
    isEditing: boolean,
    editingText: string
}>();

const emit = defineEmits<{
    (e: 'switch-sibling', direction: 'prev' | 'next'): void,
    (e: 'generate'): void,
    (e: 'start-edit'): void,
    (e: 'cancel-edit'): void,
    (e: 'save-edit', shouldGenerate: boolean): void,
    (e: 'update:editingText', value: string): void
}>();
</script>

<style scoped>
.message-tile {
    display: flex;
    gap: 16px;
    padding: 16px 0;
    border-top: 1px solid var(--border-default);
    
    /* Expand into the left margin, then pad the text back to its original spot */
    margin-left: -52px; 
    padding-left: 52px;
}

.message-tile:first-child {
    border-top: none;
    margin-top: 0;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 4px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
}

.user-role .avatar {
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}

.assistant-role .avatar {
    color: var(--accent-green);
    border-color: var(--accent-green);
}

.message-body {
    flex: 1;
    min-width: 0;
}

.message-header {
    margin-bottom: 8px;
    font-size: 17px;
    font-weight: 600;
    color: var(--text-muted);
    display: flex;
    align-items: baseline;
    gap: 8px;
}

.msg-time {
    font-size: 12px;
    font-weight: 400;
    color: var(--text-faded);
    cursor: default;
}

.user-role .message-header {
    color: var(--accent-blue);
}

.assistant-role .message-header {
    color: var(--accent-green);
}

.message-content {
    font-size: 15px;
    line-height: 1.6;
    color: var(--text-primary);
}

.message-tile.error .message-content {
    color: #fca5a5; /* Kept hex for specific error tailwind shade */
}

.placeholder {
    color: var(--text-muted);
    font-style: italic;
}

.markdown-content.streaming :deep(p:last-child)::after {
    content: '';
    display: inline-block;
    width: 8px;
    height: 16px;
    background-color: var(--accent-blue);
    margin-left: 4px; /* Increased from 2px to add a space */
    vertical-align: text-bottom;
    animation: blink 1s step-end infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* Responsive: On small screens, remove the negative margin so it doesn't overflow */
@media (max-width: 1024px) {
    .message-tile {
        margin-left: 0;
        padding-left: 0;
    }
}

/* Markdown Overrides (Global via :deep) */
.markdown-content {
    background: transparent !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

.markdown-content :deep(.md-editor-preview) {
    padding: 0 !important;
    background: transparent !important;
}

.markdown-content :deep(p),
.markdown-content :deep(li),
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
    color: var(--text-primary) !important;
}

.reasoning-content :deep(p),
.reasoning-content :deep(li),
.reasoning-content :deep(h1),
.reasoning-content :deep(h2),
.reasoning-content :deep(h3),
.reasoning-content :deep(h4) {
    color: var(--text-secondary) !important;
}

.markdown-content :deep(p) {
    margin: 0 0 10px 0;
}

.markdown-content :deep(p:last-child) {
    margin-bottom: 0;
}

.user-role .markdown-content :deep(a) {
    color: var(--text-primary);
    text-decoration: underline;
}

/* Fix md-editor-v3's aggressive word-breaking */
.markdown-content :deep(p),
.markdown-content :deep(li),
.markdown-content :deep(.md-editor-preview) {
    word-break: normal !important;
    overflow-wrap: anywhere !important;
}

/* Disable sticky code headers and fix z-index conflict with modals */
.markdown-content :deep(.md-editor-code-head) {
    position: relative !important;
    z-index: 1 !important;
}

/* Code Block Traffic Light Replacement */
.markdown-content :deep(.md-editor-code-flag span) {
    display: none !important;
}

.markdown-content :deep(.md-editor-code-flag::after) {
    content: '</>';
    color: var(--text-faded);
    font-family: monospace;
    font-size: 12px;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}
</style>