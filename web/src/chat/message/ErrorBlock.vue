<template>
    <div class="error-block">
        <div class="error-header">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.triangle_alert"></svg>
            <span>LLM Provider Error</span>
        </div>
        <pre class="error-data">{{ formattedError }}</pre>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ICONS } from '@/icons';

const props = defineProps<{
    errorData: any
}>();

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

.error-data {
    margin: 0;
    background: var(--bg-primary);
    border-radius: var(--radius-sm);
    padding: 8px;
    white-space: pre-wrap;
    word-break: break-all;
    font-family: monospace;
    font-size: 12px;
    color: var(--text-secondary);
    max-height: 300px;
    overflow-y: auto;
}
</style>