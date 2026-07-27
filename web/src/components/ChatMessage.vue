<template>
    <div class="message-row" :class="{ 'user-role': message.role === 'user', 'assistant-role': message.role === 'assistant' }">
        <div class="message-bubble" :class="{ 'streaming': message.status === 'streaming', 'error': message.status === 'error' }">
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
.message-row {
    display: flex;
    margin: 16px 0;
    width: 100%;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

.user-role {
    justify-content: flex-end;
}

.assistant-role {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 16px;
    font-size: 15px;
    line-height: 1.6;
    /* white-space: pre-wrap; */
    /* word-wrap: break-word; */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-role .message-bubble {
    background: #3b82f6;
    color: white;
    border-bottom-right-radius: 4px;
}

.assistant-role .message-bubble {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-bottom-left-radius: 4px;
}

.message-bubble.error {
    background: #450a0a;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
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

/* Override default md-editor-v3 styles to fit our chat bubble */
.markdown-content {
    background: transparent !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

.markdown-content :deep(.md-editor-preview) {
    padding: 0 !important;
    background: transparent !important;
}

/* Force light text for dark theme compatibility */
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

/* Hide the three traffic light dots, but keep the space they occupy */
.markdown-content :deep(.md-editor-code-flag span) {
    display: none !important;
}

/* Inject a replacement symbol into the flag's space */
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