<template>
    <div class="edit-area">
        <textarea 
            ref="textareaRef"
            class="edit-textarea" 
            :value="editingText" 
            @input="handleInput"
        ></textarea>
        <div class="edit-actions">
            <button v-if="role === 'user'" @click="emit('save-edit', true)" class="btn-primary">Save & Send</button>
            <button @click="emit('save-edit', false)" class="btn-secondary">Save</button>
            <button @click="emit('cancel-edit')" class="btn-ghost">Cancel</button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useAutoResizeTextarea } from '../useAutoResizeTextarea'; // <-- Import (up one level)

const props = defineProps<{ 
    editingText: string,
    role: string
}>();

const emit = defineEmits<{
    (e: 'update:editingText', value: string): void,
    (e: 'save-edit', shouldGenerate: boolean): void,
    (e: 'cancel-edit'): void
}>();

// Use composable, passing a getter for the editingText
const { textareaRef, adjustHeight } = useAutoResizeTextarea(() => props.editingText);

function handleInput(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    emit('update:editingText', target.value);
    adjustHeight();
}
</script>

<style scoped>
.edit-area {
    margin-top: 8px;
}

.edit-textarea {
    width: 100%;
    min-height: 100px;
    max-height: 300px;
    background: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    border-radius: 6px;
    padding: 12px;
    font-family: inherit;
    font-size: 15px;
    line-height: 1.6;
    box-sizing: border-box;
    resize: none; /* Disable manual resize, we handle it automatically */
    overflow-y: auto; /* Scroll when exceeding max-height */
}

.edit-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    justify-content: flex-start;
}

.btn-primary, .btn-secondary, .btn-ghost {
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.btn-primary {
    background: #3b82f6;
    border: 1px solid #3b82f6;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
    border-color: #2563eb;
}

.btn-secondary {
    background: #334155;
    border: 1px solid #475569;
    color: #e2e8f0;
}

.btn-secondary:hover {
    background: #3f4d63;
}

.btn-ghost {
    background: transparent;
    border: 1px solid transparent;
    color: #64748b;
}

.btn-ghost:hover {
    color: #cbd5e1;
    background: rgba(30, 41, 59, 0.5);
}
</style>