<template>
    <div class="prompt-tile">
        <div class="prompt-header" @click="toggleExpand" :class="{ 'editing': isEditing }">
            <svg class="chevron" :class="{ 'expanded': isExpanded || isEditing }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
            <div class="prompt-label">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="message.role === 'system' ? ICONS.settings : ICONS.terminal"></svg>
                <span>{{ message.role === 'system' ? 'System Prompt' : 'Developer Prompt' }}</span>
            </div>
        </div>
        
        <div v-if="isExpanded || isEditing" class="prompt-content">
            <EditArea 
                v-if="isEditing"
                :editingText="editingText"
                :role="message.role"
                @update:editingText="emit('update:editingText', $event)"
                @save-edit="emit('save-edit', $event)"
                @cancel-edit="emit('cancel-edit')"
            />
            <template v-else>
                <MdPreview 
                    v-if="message.content"
                    :modelValue="message.content" 
                    theme="dark" 
                    :previewTheme="'github'" 
                    :codeTheme="'github'" 
                    :language="'en-US'"
                    class="markdown-content"
                    @dblclick="handleMarkdownDblClick"
                    @copy="handleMarkdownCopy"
                />
                <span v-else class="empty-prompt">Empty prompt</span>
                
                <MessageActions 
                    :siblingInfo="siblingInfo" 
                    :isInteractive="true"
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
import { ref } from 'vue';
import { MdPreview } from 'md-editor-v3';
import { Message } from '@/types';
import EditArea from './EditArea.vue';
import MessageActions from './MessageActions.vue';
import { ICONS } from '@/icons';
import { handleMarkdownDblClick, handleMarkdownCopy } from '@/chat/markdownInteractions';

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

const isExpanded = ref(false);

function toggleExpand() {
    isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
.prompt-tile {
    margin: 12px 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    overflow: hidden;
    /* No negative margin. Box starts at the left edge of the avatar */
}

.prompt-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    cursor: pointer;
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 600;
    user-select: none;
    transition: background 0.2s;
}

.prompt-header:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.prompt-header.editing {
    cursor: default;
}

.prompt-header.editing:hover {
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

.prompt-content {
    padding: 0 16px 12px 48px;
    border-top: 1px solid var(--border-default);
    padding-top: 12px;
}

.empty-prompt {
    color: var(--text-faded);
    font-style: italic;
    font-size: 14px;
}

/* Markdown Overrides (Global via :deep) - Matches ChatMessage.vue */
.markdown-content {
    background: transparent !important;
    font-size: 14px !important;
    line-height: 1.6 !important;
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
    color: var(--text-secondary) !important;
}

.markdown-content :deep(p) {
    margin: 0 0 10px 0;
}

.markdown-content :deep(p:last-child) {
    margin-bottom: 0;
}

.markdown-content :deep(p),
.markdown-content :deep(li),
.markdown-content :deep(.md-editor-preview) {
    word-break: normal !important;
    overflow-wrap: anywhere !important;
}

.markdown-content :deep(.md-editor-code-head) {
    position: relative !important;
    z-index: 1 !important;
}

.markdown-content :deep(.md-editor-code-flag span) {
    display: none !important;
}

/* Make MessageActions visible for prompt tiles */
.prompt-content :deep(.message-footer) {
    opacity: 1;
}
</style>