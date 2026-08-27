<template>
    <details :open="!content && (status === 'pending' || status === 'streaming')" class="reasoning-block">
        <summary>
            <div class="summary-left">
                <svg class="bulb-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.lightbulb"></svg>
                <span class="reasoning-label">Thoughts</span>
                <div v-if="!content && status === 'streaming'" class="spinner small-spinner"></div>
            </div>
            <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
        </summary>
        <MdPreview 
            :modelValue="reasoning" 
            theme="dark" 
            :previewTheme="'github'" 
            :codeTheme="'github'" 
            :language="'en-US'"
            class="markdown-content reasoning-content"
            @dblclick="handleMarkdownDblClick"
            @copy="handleMarkdownCopy"
        />
    </details>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';
import { ICONS } from '@/icons';
import { handleMarkdownDblClick, handleMarkdownCopy } from '@/chat/markdownInteractions';

defineProps<{ 
    reasoning: string,
    status: string,
    content: string | null
}>();
</script>

<style scoped>
.reasoning-block {
    margin-bottom: 16px;
}

.reasoning-block summary {
    cursor: pointer;
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px; /* Use gap to space out label and chevron */
    margin-bottom: 0;
    padding: 4px 0; /* Remove horizontal padding to align with content */
    transition: background 0.2s;
    user-select: none; /* Prevent text selection on rapid clicks */
}

.summary-left {
    display: flex;
    align-items: center;
    gap: 6px;
}

.reasoning-block summary::-webkit-details-marker {
    display: none;
}

.chevron-icon {
    color: var(--text-faded);
    transition: transform 0.2s ease;
    flex-shrink: 0;
}

.reasoning-block[open] .chevron-icon {
    transform: rotate(90deg);
}

.bulb-icon {
    color: var(--accent-yellow);
    flex-shrink: 0;
}

.small-spinner {
    width: 12px;
    height: 12px;
    border-width: 1.5px;
}

.reasoning-content {
    margin-top: 8px;
    border-left: 2px solid var(--border-default);
    padding-left: 16px;
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: var(--radius-sm);
    background: rgba(15, 23, 42, 0.5); 
    font-size: 14px;
    color: var(--text-secondary);
    opacity: 0.8;
}

/* === md-editor-v3 Overrides (Targeting child component internals via :deep) === */
.reasoning-content {
    background: transparent !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

.reasoning-content :deep(.md-editor-preview) {
    padding: 0 !important;
    background: transparent !important;
}

/* KaTeX \tag: katex.css abs-positions it, escaping the scroll container and
   pinning to the screen edge (overlaps the formula, doesn't scroll with it).
   In-flow: same nowrap line, right after the formula. */
.markdown-content :deep(.katex-html > .tag) {
    position: static !important;
    margin-left: 1em;
}

.reasoning-content :deep(p) {
    margin: 0 0 10px 0;
}

/* This is the specific fix for the "extra newline" */
.reasoning-content :deep(p:last-child) {
    margin-bottom: 0;
}

.reasoning-content :deep(p),
.reasoning-content :deep(li),
.reasoning-content :deep(.md-editor-preview) {
    word-break: normal !important;
    overflow-wrap: anywhere !important;
}

.reasoning-content :deep(.md-editor-code-head) {
    position: relative !important;
    z-index: 1 !important;
}

.reasoning-content :deep(.md-editor-code-flag span) {
    display: none !important;
}

.reasoning-content :deep(.md-editor-code-flag::after) {
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