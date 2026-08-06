<template>
    <div class="message-details">
        <div v-if="creationData" class="detail-section">
            <span class="detail-label">Creation Data</span>
            <pre>{{ formattedCreationData }}</pre>
        </div>
        <div v-if="metadata" class="detail-section">
            <span class="detail-label">Metadata</span>
            <pre>{{ formattedMetadata }}</pre>
        </div>
        <div v-if="!creationData && !metadata" class="empty-details">
            No details available.
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
    creationData?: any,
    metadata?: any
}>();

const formattedCreationData = computed(() => JSON.stringify(props.creationData, null, 2));
const formattedMetadata = computed(() => JSON.stringify(props.metadata, null, 2));
</script>

<style scoped>
.message-details {
    margin-top: 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 12px;
    font-size: 13px;
    color: var(--text-secondary);
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-section {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.detail-label {
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.05em;
}

pre {
    margin: 0;
    padding: 8px;
    background: var(--bg-primary);
    border-radius: var(--radius-sm);
    white-space: pre-wrap;
    word-break: break-all;
    font-family: monospace;
    color: var(--text-primary);
    max-height: 300px;
    overflow-y: auto;
}

.empty-details {
    color: var(--text-faded);
    font-style: italic;
}
</style>