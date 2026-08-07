<template>
    <div class="error-block">
        <div class="error-header">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.triangle_alert"></svg>
            <span>LLM Provider Error</span>
            <span class="error-type">{{ errorType }}</span>
        </div>
        <div class="error-message">{{ errorMessage }}</div>
        
        <!-- Collapsible raw data for deep debugging -->
        <details class="raw-error" v-if="errorData">
            <summary>Raw Error Data</summary>
            <pre>{{ formattedError }}</pre>
        </details>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ICONS } from '@/icons';

const props = defineProps<{
    errorData: any
}>();

const errorType = computed(() => props.errorData?.type || 'Unknown');

const errorMessage = computed(() => {
    const body = props.errorData?.body;
    if (!body) {
        // Fallback for internal BOUGH errors or missing body
        return props.errorData?.message || 'Unknown error';
    }
    
    // Extract the most useful message from OpenRouter's nested structure
    return body?.metadata?.raw 
        || body?.error?.message 
        || body?.message 
        || props.errorData?.message 
        || 'Unknown error';
});

const formattedError = computed(() => {
    if (!props.errorData) return 'No error data provided.';
    try {
        return JSON.stringify(props.errorData, null, 2);
    } catch (e) {
        return String(props.errorData);
    }
});
</script>

<style scoped>
.error-block {
    margin-top: 12px;
    background: rgba(239, 68, 68, 0.1); /* Muted red background */
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    color: #fca5a5; /* Error text color */
    font-size: 14px;
}

.error-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    margin-bottom: 8px;
}

.error-type {
    font-size: 11px;
    font-weight: 400;
    color: rgba(252, 165, 165, 0.7);
    background: rgba(239, 68, 68, 0.2);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
}

.error-message {
    color: var(--text-primary);
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 8px;
}

.raw-error {
    margin-top: 8px;
}

.raw-error summary {
    cursor: pointer;
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
    user-select: none;
    margin-bottom: 4px;
}

.raw-error summary:hover {
    color: var(--text-secondary);
}

.raw-error pre {
    margin: 0;
    background: var(--bg-primary);
    border-radius: var(--radius-sm);
    padding: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: monospace;
    font-size: 12px;
    color: var(--text-secondary);
    max-height: 200px;
    overflow-y: auto;
}
</style>