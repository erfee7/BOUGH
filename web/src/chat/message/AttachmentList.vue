<template>
    <div v-if="attachments.length" class="attachment-list">
        <template v-for="att in attachments" :key="att.id">
            <button
                v-if="att.mime_type.startsWith('image/')"
                class="image-link"
                :title="att.filename"
                @click="previewing = att"
            >
                <img class="attachment-image" :src="attachmentUrl(att.id)" :alt="att.filename" />
            </button>
            <button
                v-else
                class="file-chip"
                :title="att.filename"
                @click="previewing = att"
            >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.file_text"></svg>
                <span class="file-name">{{ att.filename }}</span>
                <span class="file-size">{{ formatFileSize(att.size) }}</span>
            </button>
        </template>
    </div>
    <AttachmentPreview v-if="previewing" :attachment="previewing" @close="previewing = null" />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AttachmentPreview from './AttachmentPreview.vue';
import { AttachmentMeta } from '@/types';
import { ICONS } from '@/icons';
import { formatFileSize } from '@/utils/format';

const previewing = ref<AttachmentMeta | null>(null);

defineProps<{
    attachments: AttachmentMeta[]
}>();

function attachmentUrl(id: string): string {
    return `/api/chat/attachments/${id}`;
}
</script>

<style scoped>
.attachment-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.image-link {
    display: inline-block;
    background: none;
    padding: 0;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    overflow: hidden;
    cursor: zoom-in;
}

.attachment-image {
    display: block;
    max-height: 200px;
    max-width: 100%;
    object-fit: contain;
}

.file-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    max-width: 260px;
    padding: 6px 10px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
}

.file-chip:hover {
    border-color: var(--accent-blue);
}

.file-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-size {
    color: var(--text-faded);
    white-space: nowrap;
}
</style>