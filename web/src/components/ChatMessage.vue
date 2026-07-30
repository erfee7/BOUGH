<template>
    <div class="message-tile" :class="{ 'user-role': message.role === 'user', 'assistant-role': message.role === 'assistant', 'error': message.status === 'error' }">
        <div class="avatar">
            <svg v-if="message.role === 'user'" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2l2.5 7L22 12l-7.5 3L12 22l-2.5-7L2 12l7.5-3z"></path></svg>
        </div>
        <div class="message-body">
            <div class="message-header">
                <span class="role-label">{{ message.role === 'user' ? 'User' : 'Assistant' }}</span>
                <div v-if="siblingInfo.count > 1" class="sibling-nav">
                    <button @click="emit('switch-sibling', 'prev')" :disabled="siblingInfo.currentIndex === 0">‹</button>
                    <span>{{ siblingInfo.currentIndex + 1 }}/{{ siblingInfo.count }}</span>
                    <button @click="emit('switch-sibling', 'next')" :disabled="siblingInfo.currentIndex === siblingInfo.count - 1">›</button>
                </div>
            </div>
            
            <!-- Edit Mode -->
            <div v-if="isEditing" class="edit-area">
                <textarea 
                    class="edit-textarea" 
                    :value="editingText" 
                    @input="emit('update:editingText', ($event.target as HTMLTextAreaElement).value)"
                ></textarea>
                <div class="edit-actions">
                    <button @click="emit('cancel-edit')" class="btn-secondary">Cancel</button>
                    <button @click="emit('save-edit', false)" class="btn-secondary">Save</button>
                    <button v-if="message.role === 'user'" @click="emit('save-edit', true)" class="btn-primary">Save & Submit</button>
                </div>
            </div>

            <!-- Normal Mode -->
            <template v-else>
                <details v-if="message.reasoning" :open="!message.content && (message.status === 'pending' || message.status === 'streaming')" class="reasoning-block">
                    <summary>
                        <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"></path></svg>
                        <svg class="bulb-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h2"></path></svg>
                        <span class="reasoning-label">Thoughts</span>
                        <svg v-if="!message.content && message.status === 'streaming'" class="spinner-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
                    </summary>
                    <MdPreview 
                        :modelValue="message.reasoning" 
                        theme="dark" 
                        :previewTheme="'github'" 
                        :codeTheme="'github'" 
                        :language="'en-US'"
                        class="markdown-content reasoning-content"
                    />
                </details>

                <div class="message-content">
                    <MdPreview 
                        v-if="message.content"
                        :modelValue="message.content" 
                        theme="dark" 
                        :previewTheme="'github'" 
                        :codeTheme="'github'" 
                        :language="'en-US'"
                        class="markdown-content"
                    />
                    <span v-else-if="message.status === 'pending' || message.status === 'streaming'" class="placeholder">Thinking...</span>
                    <span v-else>Empty</span>
                    
                    <span v-if="message.status === 'streaming' && message.content" class="cursor">▋</span>
                </div>

                <div class="message-actions">
                    <button @click="emit('start-edit')" class="btn-action">Edit</button>
                    <button @click="emit('generate')" :disabled="isStreaming" class="btn-action">
                        {{ message.role === 'user' ? 'Generate Response' : 'Continue' }}
                    </button>
                </div>
            </template>
        </div>
    </div>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import { Message } from '../types';

defineProps<{ 
    message: Message,
    siblingInfo: { count: number, currentIndex: number },
    isStreaming: boolean,
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
    margin: 24px 0;
    padding: 16px 0;
    border-top: 1px solid #1e293b;
    
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
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 4px; /* Align roughly with the header text */
    background: #1e293b;
    border: 1px solid #334155;
}

.user-role .avatar {
    color: #3b82f6;
    border-color: #3b82f6;
}

.assistant-role .avatar {
    color: #10b981;
    border-color: #10b981;
}

.message-body {
    flex: 1;
    min-width: 0; /* Prevents markdown content from overflowing */
}

.message-header {
    margin-bottom: 8px;
    font-size: 17px;
    font-weight: 600;
    color: #94a3b8;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-role .message-header {
    color: #3b82f6;
}

.assistant-role .message-header {
    color: #10b981;
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

/* Responsive: On small screens, remove the negative margin so it doesn't overflow */
@media (max-width: 1024px) {
    .message-tile {
        margin-left: 0;
        padding-left: 0;
    }
}

/* Reasoning Block Styles */
.reasoning-block {
    margin-bottom: 16px;
    /* Removed border-left, padding-left, border-radius from here */
}

.reasoning-block summary {
    cursor: pointer;
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 0; /* Changed to 0 so the box below controls the spacing */
}

.reasoning-block summary::-webkit-details-marker {
    display: none; /* Hide default arrow */
}

.chevron-icon {
    color: #64748b;
    transition: transform 0.2s ease; /* Smooth rotation */
    flex-shrink: 0;
}

/* Rotate the chevron 90 degrees when the details block is open */
.reasoning-block[open] .chevron-icon {
    transform: rotate(90deg);
}

.bulb-icon {
    color: #fbbf24;
    flex-shrink: 0;
}

.spinner-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Apply the visual wrapper to the content instead of the whole block */
.reasoning-content {
    margin-top: 8px; /* Give space from the summary above */
    border-left: 2px solid #334155;
    padding-left: 16px;
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: 4px;
    /* Add a very subtle dark background to make it feel like a contained block */
    background: rgba(15, 23, 42, 0.5); 
    font-size: 14px;
    color: #cbd5e1;
    opacity: 0.8;
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

.reasoning-content :deep(p),
.reasoning-content :deep(li),
.reasoning-content :deep(h1),
.reasoning-content :deep(h2),
.reasoning-content :deep(h3),
.reasoning-content :deep(h4) {
    color: #cbd5e1 !important;
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

/* Message Branching */
.sibling-nav {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    color: #94a3b8;
    margin-left: auto;
}

.sibling-nav button {
    background: none;
    border: none;
    color: #94a3b8;
    cursor: pointer;
    padding: 0 4px;
    font-size: 16px;
}

.sibling-nav button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.message-actions {
    margin-top: 16px;
    display: flex;
    gap: 8px;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.message-tile:hover .message-actions {
    opacity: 1;
}

.btn-action {
    background: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
}

.btn-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.edit-area {
    margin-top: 8px;
}

.edit-textarea {
    width: 100%;
    min-height: 100px;
    background: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    border-radius: 6px;
    padding: 12px;
    font-family: inherit;
    font-size: 15px;
    line-height: 1.6;
    box-sizing: border-box;
    resize: vertical;
}

.edit-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}

.btn-secondary, .btn-primary {
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}

.btn-secondary {
    background: #334155;
    border: 1px solid #475569;
    color: #f8fafc;
}

.btn-primary {
    background: #3b82f6;
    border: 1px solid #3b82f6;
    color: white;
}
</style>