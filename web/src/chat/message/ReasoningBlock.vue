<template>
    <details :open="!content && (status === 'pending' || status === 'streaming')" class="reasoning-block">
        <summary>
            <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
            <svg class="bulb-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.lightbulb"></svg>
            <span class="reasoning-label">Thoughts</span>
            <div v-if="!content && status === 'streaming'" class="spinner small-spinner"></div>
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
    gap: 6px;
    margin-bottom: 0;
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
</style>