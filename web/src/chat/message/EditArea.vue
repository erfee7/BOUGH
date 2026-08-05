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
import { useAutoResizeTextarea } from '@/chat/useAutoResizeTextarea';

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
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    color: var(--text-primary);
    border-radius: var(--radius-md);
    padding: 12px;
    font-family: inherit;
    font-size: 15px;
    line-height: 1.6;
    box-sizing: border-box;
    resize: none; /* Disable manual resize, we handle it automatically */
    overflow-y: auto; /* Scroll when exceeding max-height */
    outline: none;
}

.edit-textarea:focus {
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.edit-actions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    justify-content: flex-start;
}
</style>