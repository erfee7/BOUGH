<template>
    <details :open="!content && (status === 'pending' || status === 'streaming')" class="reasoning-block">
        <summary>
            <svg class="chevron-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"></path></svg>
            <svg class="bulb-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h2"></path></svg>
            <span class="reasoning-label">Thoughts</span>
            <svg v-if="!content && status === 'streaming'" class="spinner-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
        </summary>
        <MdPreview 
            :modelValue="reasoning" 
            theme="dark" 
            :previewTheme="'github'" 
            :codeTheme="'github'" 
            :language="'en-US'"
            class="markdown-content reasoning-content"
        />
    </details>
</template>

<script setup lang="ts">
import { MdPreview } from 'md-editor-v3';

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
    color: #94a3b8;
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
    color: #64748b;
    transition: transform 0.2s ease;
    flex-shrink: 0;
}

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

.reasoning-content {
    margin-top: 8px;
    border-left: 2px solid #334155;
    padding-left: 16px;
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: 4px;
    background: rgba(15, 23, 42, 0.5); 
    font-size: 14px;
    color: #cbd5e1;
    opacity: 0.8;
}
</style>