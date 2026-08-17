<template>
    <Teleport to="body">
        <div class="preview-backdrop" @click="emit('close')">
            <img
                v-if="isImage"
                class="preview-image"
                :src="url"
                :alt="attachment.filename"
                @click.stop
            />
            <iframe
                v-else
                class="preview-frame"
                :src="url"
                :title="attachment.filename"
            ></iframe>
            <div class="preview-caption" @click.stop>
                <span class="caption-name" :title="attachment.filename">{{ attachment.filename }}</span>
                <span class="caption-size">{{ formatFileSize(attachment.size) }}</span>
                <a :href="url" target="_blank" rel="noopener" class="caption-link">Open original</a>
                <button class="caption-close" title="Close (Esc)" @click="emit('close')">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                </button>
            </div>
        </div>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import { AttachmentMeta } from '@/types';
import { ICONS } from '@/icons';
import { formatFileSize } from '@/utils/format';

const props = defineProps<{
    attachment: AttachmentMeta
}>();

const emit = defineEmits<{
    (e: 'close'): void
}>();

// Images render as <img>; everything else (PDFs today, audio/video naturally later)
// renders in an <iframe>, where the browser applies its own native handling.
const isImage = computed(() => props.attachment.mime_type.startsWith('image/'));
const url = computed(() => `/api/chat/attachments/${props.attachment.id}`);

function onKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') emit('close');
}

// Lock body scroll while open; restore whatever was there before, honestly
let savedOverflow = '';
onMounted(() => {
    document.addEventListener('keydown', onKeydown);
    savedOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
});
onUnmounted(() => {
    document.removeEventListener('keydown', onKeydown);
    document.body.style.overflow = savedOverflow;
});
</script>

<style scoped>
.preview-backdrop {
    position: fixed;
    inset: 0;
    z-index: 10000;
    background: rgba(0, 0, 0, 0.82);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    animation: preview-fade 0.15s ease;
}

@keyframes preview-fade {
    from { opacity: 0; }
    to { opacity: 1; }
}

.preview-image {
    max-width: 90vw;
    max-height: 85vh;
    object-fit: contain;
    border-radius: var(--radius-md);
}

.preview-frame {
    width: 85vw;
    height: 85vh;
    border: none;
    border-radius: var(--radius-md);
    background: var(--bg-primary);
}

.preview-caption {
    display: flex;
    align-items: center;
    gap: 12px;
    max-width: 90vw;
    padding: 6px 12px;
    border-radius: var(--radius-md);
    background: rgba(0, 0, 0, 0.6);
    color: var(--text-muted);
    font-size: 13px;
}

.caption-name {
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.caption-size {
    color: var(--text-faded);
    white-space: nowrap;
}

.caption-link {
    color: var(--accent-blue);
    text-decoration: none;
    white-space: nowrap;
}

.caption-link:hover {
    text-decoration: underline;
}

.caption-close {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    padding: 2px;
    cursor: pointer;
    color: var(--text-muted);
}

.caption-close:hover {
    color: var(--text-primary);
}
</style>