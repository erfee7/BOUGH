<template>
    <div class="input-area">
        <div v-if="showDevPrompt" class="dev-prompt-panel">
            <PromptSelector 
                role="developer" 
                :modelValue="developerPrompt" 
                @update:modelValue="emit('update:developerPrompt', $event)"
                @openLibrary="emit('openLibrary')"
            />
        </div>
        
        <div class="action-bar">
            <button @click="toggleDevPrompt" class="btn-icon toggle-dev-btn" :class="{ 'active': showDevPrompt }" title="Toggle Developer Prompt">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.terminal"></svg>
            </button>
            <button @click="fileInputRef?.click()" class="btn-icon" title="Attach files">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.paperclip"></svg>
            </button>
            <input
                ref="fileInputRef"
                type="file"
                multiple
                accept="image/png,image/jpeg,image/webp,image/gif,application/pdf"
                class="hidden-file-input"
                @change="onFilesChosen"
            />
        </div>

        <div
            class="input-container"
            :class="{ 'drag-over': isDragOver }"
            @dragenter="onDragEnter"
            @dragover.prevent
            @dragleave="onDragLeave"
            @drop.prevent="onDrop"
        >
            <div v-if="drafts.length" class="attachment-drafts">
                <div
                    v-for="d in drafts"
                    :key="d.localId"
                    class="draft-chip"
                    :class="{ 'error': d.status === 'error', 'clickable': d.status === 'done' }"
                    @click="openDraftPreview(d)"
                >
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="d.file.type === 'application/pdf' ? ICONS.file_text : ICONS.image"></svg>
                    <span class="chip-name" :title="d.file.name">{{ d.file.name }}</span>
                    <span v-if="d.status === 'uploading'" class="spinner chip-spinner"></span>
                    <span v-else-if="d.status === 'error'" class="chip-sub error-text">{{ d.error }}</span>
                    <span v-else class="chip-sub">{{ d.file.type }} · {{ d.meta ? formatFileSize(d.meta.size) : formatFileSize(d.file.size) }}</span>
                    <button v-if="d.status === 'error'" class="chip-btn" title="Retry upload" @click.stop="emit('retry-draft', d.localId)">
                        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.rotate_cw"></svg>
                    </button>
                    <button class="chip-btn" title="Remove" @click.stop="emit('remove-draft', d.localId)">
                        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                    </button>
                </div>
            </div>

            <div class="input-row">
                <textarea 
                    ref="textareaRef"
                    :value="modelValue" 
                    @input="handleInput"
                    @keydown.enter.exact.prevent="handleSend"
                    @paste="handlePaste"
                    placeholder="Type a message... (Enter to send)"
                ></textarea>
                <button v-if="!isStreaming" @click="handleSend" :disabled="!canSend" class="send-btn">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.send"></svg>
                </button>
                <button v-else @click="emit('cancel')" class="stop-btn">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.square"></svg>
                </button>
            </div>
        </div>
        <AttachmentPreview v-if="previewing" :attachment="previewing" @close="previewing = null" />
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import PromptSelector from './prompts/PromptSelector.vue';
import AttachmentPreview from './message/AttachmentPreview.vue';
import { useAutoResizeTextarea } from './useAutoResizeTextarea';
import { formatFileSize } from '@/utils/format';
import { AttachmentDraft, AttachmentMeta } from '@/types';
import { ICONS } from '@/icons';

const props = defineProps<{ 
    modelValue: string, 
    isStreaming: boolean,
    developerPrompt: string,
    drafts: AttachmentDraft[]
}>();

const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'update:developerPrompt', value: string): void,
    (e: 'send'): void,
    (e: 'cancel'): void,
    (e: 'openLibrary'): void,
    (e: 'files-added', files: File[]): void,
    (e: 'remove-draft', localId: string): void,
    (e: 'retry-draft', localId: string): void
}>();

const showDevPrompt = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const isDragOver = ref(false);
let dragDepth = 0;

// Presentational logic only, derived purely from props (engine guards independently)
const hasReadyAttachment = computed(() => props.drafts.some(d => d.status === 'done'));
const anyUploading = computed(() => props.drafts.some(d => d.status === 'uploading'));
const canSend = computed(() => (props.modelValue.trim().length > 0 || hasReadyAttachment.value) && !anyUploading.value);

const { textareaRef, adjustHeight } = useAutoResizeTextarea(() => props.modelValue);

const previewing = ref<AttachmentMeta | null>(null);

// Only completed drafts have a server blob to preview; uploading/error chips stay inert
function openDraftPreview(draft: AttachmentDraft) {
    if (draft.status === 'done' && draft.meta) previewing.value = draft.meta;
}

function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    emit('update:modelValue', target.value);
    adjustHeight();
}

function toggleDevPrompt() {
    showDevPrompt.value = !showDevPrompt.value;
    // If hiding the panel, clear the prompt text so it doesn't get sent invisibly
    if (!showDevPrompt.value) {
        emit('update:developerPrompt', '');
    }
}

function handleSend() {
    if (!canSend.value) return;
    emit('send');
    showDevPrompt.value = false;
}

// --- File intake: picker, drag & drop, paste ---

function onFilesChosen(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) emit('files-added', Array.from(input.files));
    input.value = ''; // Allow re-choosing the same file
}

function onDragEnter(event: DragEvent) {
    event.preventDefault();
    dragDepth++;
    isDragOver.value = true;
}

function onDragLeave() {
    dragDepth--;
    if (dragDepth <= 0) {
        dragDepth = 0;
        isDragOver.value = false;
    }
}

function onDrop(event: DragEvent) {
    dragDepth = 0;
    isDragOver.value = false;
    const files = Array.from(event.dataTransfer?.files ?? []);
    if (files.length) emit('files-added', files);
}

function handlePaste(event: ClipboardEvent) {
    const files = Array.from(event.clipboardData?.files ?? []);
    if (files.length) {
        event.preventDefault(); // Files found in the clipboard: attach instead of pasting as text
        emit('files-added', files);
    }
}
</script>

<style scoped>
.input-area {
    flex-shrink: 0;
    padding: 20px 2% 32px;
}

@media (max-width: 1024px) {
    .input-area {
        padding: 20px 16px 32px;
    }
}

.dev-prompt-panel {
    margin-bottom: 12px;
}

.action-bar {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 8px;
}

.toggle-dev-btn.active {
    background: var(--bg-tertiary);
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}

.hidden-file-input {
    display: none;
}

.input-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}

.input-container.drag-over {
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.input-row {
    display: flex;
    align-items: flex-end;
}

.input-row textarea {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 15px;
    line-height: 1.5;
    max-height: 200px;
    min-height: 24px;
    padding: 0 8px;
    resize: none;
    outline: none;
    overflow-y: auto; /* Show scrollbar when content exceeds max height */
}

.attachment-drafts {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.draft-chip {
    display: flex;
    align-items: center;
    gap: 6px;
    max-width: 260px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 4px 8px;
    font-size: 12px;
    color: var(--text-muted);
}

.draft-chip.error {
    border-color: var(--accent-red);
}

.chip-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--text-primary);
}

.chip-sub {
    color: var(--text-faded);
    white-space: nowrap;
}

.chip-sub.error-text {
    color: var(--accent-red);
}

.chip-spinner {
    width: 12px;
    height: 12px;
}

.chip-btn {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    color: var(--text-muted);
}

.chip-btn:hover {
    color: var(--text-primary);
}

.input-container:focus-within {
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.send-btn, .stop-btn {
    border: none;
    border-radius: var(--radius-md);
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 36px;
    width: 36px;
    margin-left: 8px;
    transition: background-color 0.2s, transform 0.1s, opacity 0.2s;
}

.send-btn {
    background: var(--accent-blue);
}

.send-btn:hover:not(:disabled) {
    background: var(--accent-blue-hover);
    transform: translateY(-1px);
}

.send-btn:disabled {
    background: var(--bg-tertiary);
    cursor: not-allowed;
    opacity: 0.7;
}

.stop-btn {
    background: var(--accent-red);
}

.stop-btn:hover {
    background: var(--accent-red-hover);
    transform: translateY(-1px);
}

.draft-chip.clickable {
    cursor: pointer;
}

.draft-chip.clickable:hover {
    border-color: var(--accent-blue);
}
</style>