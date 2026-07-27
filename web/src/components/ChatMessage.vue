<template>
    <div class="message-tile" :class="{ 'user-role': message.role === 'user', 'assistant-role': message.role === 'assistant', 'error': message.status === 'error' }">
        <div class="message-header">
            <span class="role-label">{{ message.role === 'user' ? 'You' : 'Assistant' }}</span>
        </div>
        <div class="message-content">
            <MdPreview 
                v-if="message.content"
                :modelValue="message.content" 
                theme="dark" 
                :previewTheme="'github'" 
                :codeTheme="'atom'"
                :language="'en-US'"
                class="markdown-content"
            />
            <span v-else-if="message.status === 'pending' || message.status === 'streaming'" class="placeholder">Thinking...</span>
            <span v-else>Empty</span>
            
            <span v-if="message.status === 'streaming'" class="cursor">▋</span>
        </div>
    </div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import { Message } from '../types'; 

defineProps<{ message: Message }>();
</script>

<style scoped>
.message-tile {
    margin: 24px 0;
    padding: 16px 0;
    border-top: 1px solid #1e293b;
}

.message-tile:first-child {
    border-top: none;
    margin-top: 0;
}

.message-header {
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.user-role .message-header {
    color: #3b82f6;
}

.assistant-role .message-header {
    color: #10b981; /* Emerald green for AI */
}

.message-content {
    font-size: 15px;
    line-height: 1.6;
    color: #f8fafc;
}

.message-tile.error .message-content {
    color: #fca5a5;
}

.placeholder {
    color: #94a3b8;
    font-style: italic;
}

.cursor {
    animation: blink 1s step-end infinite;
    margin-left: 2px;
    color: #3b82f6;
}

@keyframes blink {
    0%, 100% { opacity: 0; }
    50% { opacity: 1; }
}

/* Markdown Overrides */
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
    color: #f8fafc !important;
}

.markdown-content :deep(p) {
    margin: 0 0 10px 0;
}

.markdown-content :deep(p:last-child) {
    margin-bottom: 0;
}

.user-role .markdown-content :deep(a) {
    color: #f8fafc;
    text-decoration: underline;
}

/* Code Block Traffic Light Replacement */
.markdown-content :deep(.md-editor-code-flag span) {
    display: none !important;
}

.markdown-content :deep(.md-editor-code-flag::after) {
    content: '</>';
    color: #64748b;
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