<template>
    <div 
        class="message-tile" 
        :class="{ 
            'is-prompt': isPrompt, 
            'user-role': !isPrompt && message.role === 'user', 
            'assistant-role': !isPrompt && message.role === 'assistant', 
            'error': !isPrompt && message.status === 'error' 
        }"
    >
        <!-- Avatar (Only for standard messages) -->
        <div v-if="!isPrompt" class="avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.user"></svg>
            <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.bot"></svg>
        </div>
        
        <div class="message-body">
            <!-- Header -->
            <div 
                class="message-header" 
                :class="{ 'prompt-header': isPrompt, 'editing': isEditing }"
                @click="isPrompt && !isEditing ? toggleExpand() : null"
            >
                <template v-if="isPrompt">
                    <svg class="chevron" :class="{ 'expanded': isExpanded || isEditing }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
                    <div class="prompt-label">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="message.role === 'system' ? ICONS.settings : ICONS.terminal"></svg>
                        <span>{{ message.role === 'system' ? 'System Prompt' : 'Developer Prompt' }}</span>
                        <span v-if="isExpanded" class="msg-time" :title="formatAbsoluteTime(message.created_at)">{{ formatRelativeTime(message.created_at) }}</span>
                    </div>
                </template>
                <template v-else>
                    <span class="role-label">{{ message.role === 'user' ? 'User' : 'Assistant' }}</span>
                    <span class="msg-time" :title="formatAbsoluteTime(message.created_at)">{{ formatRelativeTime(message.created_at) }}</span>
                </template>
            </div>
            
            <!-- Content Area -->
            <div 
                v-if="!isPrompt || isExpanded || isEditing" 
                class="content-wrapper" 
                :class="{ 'prompt-content': isPrompt }"
            >
                <EditArea 
                    v-if="isEditing"
                    :editingText="editingText"
                    :role="message.role"
                    @update:editingText="emit('update:editingText', $event)"
                    @save-edit="emit('save-edit', $event)"
                    @cancel-edit="emit('cancel-edit')"
                />
                <template v-else>
                    <ReasoningBlock 
                        v-if="!isPrompt && message.reasoning" 
                        :reasoning="message.reasoning" 
                        :status="message.status" 
                        :content="message.content"
                    />
                    <div class="message-content" :class="{ 'prompt-markdown': isPrompt }">
                        <MdPreview 
                            v-if="message.content"
                            :modelValue="message.content" 
                            theme="dark" 
                            :previewTheme="'github'" 
                            :codeTheme="'github'" 
                            :language="'en-US'"
                            :class="`markdown-content ${!isPrompt && message.status === 'streaming' && message.content ? 'streaming' : ''}`"
                            @dblclick="handleMarkdownDblClick"
                            @copy="handleMarkdownCopy"
                        />
                        <span v-else-if="!isPrompt && (message.status === 'pending' || message.status === 'streaming')" class="placeholder">Thinking...</span>
                        <span v-else-if="isPrompt" class="empty-prompt">Empty prompt</span>
                        <span v-else>Empty</span>
                    </div>
                    <MessageActions 
                        :siblingInfo="siblingInfo" 
                        :isInteractive="isPrompt || message.status === 'complete' || message.status === 'canceled'"
                        :role="message.role"
                        :content="message.content"
                        @switch-sibling="emit('switch-sibling', $event)"
                        @start-edit="emit('start-edit')"
                        @generate="emit('generate')"
                    />
                </template>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { MdPreview } from 'md-editor-v3';
import { Message } from '@/types';
import EditArea from './EditArea.vue';
import ReasoningBlock from './ReasoningBlock.vue';
import MessageActions from './MessageActions.vue';
import { ICONS } from '@/icons';
import { handleMarkdownDblClick, handleMarkdownCopy } from '@/chat/markdownInteractions';
import { formatRelativeTime, formatAbsoluteTime } from '@/utils/time';

const props = defineProps<{ 
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

const isPrompt = computed(() => props.message.role === 'system' || props.message.role === 'developer');
const isExpanded = ref(false);

function toggleExpand() {
    isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
/* === Base Tile (Shared) === */
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

/* === Standard Message Specifics === */
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

/* === Prompt Tile Overrides === */
.message-tile.is-prompt {
    display: block;
    margin: 12px 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    overflow: hidden;
    padding: 0;
    margin-left: 0;
    padding-left: 0;
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

.message-header.prompt-header {
    cursor: pointer;
    font-size: 14px;
    padding: 10px 16px;
    align-items: center;
    transition: background 0.2s;
}

.message-header.prompt-header:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.message-header.prompt-header.editing {
    cursor: default;
}

.message-header.prompt-header.editing:hover {
    background: transparent;
    color: var(--text-muted);
}

.chevron {
    transition: transform 0.2s ease;
}

.chevron.expanded {
    transform: rotate(90deg);
}

.prompt-label {
    display: flex;
    align-items: center;
    gap: 8px;
}

.content-wrapper.prompt-content {
    padding: 0 16px 12px 48px;
    border-top: 1px solid var(--border-default);
    padding-top: 12px;
}

.content-wrapper.prompt-content :deep(.message-footer) {
    opacity: 1;
}

.msg-time {
    font-size: 12px;
    font-weight: 400;
    color: var(--text-faded);
    cursor: default;
    
    /* Hide by default */
    opacity: 0;
    transition: opacity 0.2s ease;
}

/* Show on hover for standard messages */
.message-tile:hover .msg-time {
    opacity: 1;
}

/* Show on hover for prompt headers */
.message-header.prompt-header:hover .msg-time {
    opacity: 1;
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

.error .message-content {
    color: #fca5a5; /* Kept hex for specific error tailwind shade */
}

.placeholder {
    color: var(--text-muted);
    font-style: italic;
}

.empty-prompt {
    color: var(--text-faded);
    font-style: italic;
    font-size: 14px;
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
    .message-tile:not(.is-prompt) {
        margin-left: 0;
        padding-left: 0;
    }
}

/* === md-editor-v3 Overrides (Targeting child component internals via :deep) === */
.markdown-content {
    background: transparent !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

.markdown-content :deep(.md-editor-preview) {
    padding: 0 !important;
    background: transparent !important;
}

/* Markdown Color Rules */
.markdown-content:not(.prompt-markdown) :deep(p),
.markdown-content:not(.prompt-markdown) :deep(li),
.markdown-content:not(.prompt-markdown) :deep(h1),
.markdown-content:not(.prompt-markdown) :deep(h2),
.markdown-content:not(.prompt-markdown) :deep(h3),
.markdown-content:not(.prompt-markdown) :deep(h4) {
    color: var(--text-primary) !important;
}

.prompt-markdown :deep(p),
.prompt-markdown :deep(li),
.prompt-markdown :deep(h1),
.prompt-markdown :deep(h2),
.prompt-markdown :deep(h3),
.prompt-markdown :deep(h4) {
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