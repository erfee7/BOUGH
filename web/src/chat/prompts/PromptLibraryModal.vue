<template>
    <div v-if="isVisible" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Prompt Library</h2>
                <button @click="emit('close')" class="btn-icon close-btn" title="Close">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                </button>
            </div>
            
            <div class="modal-body">
                <div class="create-form">
                    <h3>Create New Prompt</h3>
                    <input v-model="newPrompt.name" placeholder="Name" class="text-input" />
                    <select v-model="newPrompt.role" class="text-input">
                        <option value="system">System</option>
                        <option value="developer">Developer</option>
                    </select>
                    <textarea v-model="newPrompt.content" placeholder="Prompt content..." class="text-area"></textarea>
                    <input v-model="newPrompt.description" placeholder="Description (optional)" class="text-input" />
                    <button @click="handleCreate" class="btn-primary create-btn">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.save"></svg>
                        Create
                    </button>
                </div>

                <div class="prompt-list-container">
                    <h3>Saved Prompts</h3>
                    <ul class="prompt-list">
                        <li v-for="p in promptStore.prompts" :key="p.id" class="prompt-item">
                            <div v-if="editingId !== p.id" class="prompt-view">
                                <div class="prompt-info">
                                    <strong>{{ p.name }}</strong> <span class="role-tag">{{ p.role }}</span>
                                    <p v-if="p.description" class="prompt-desc">{{ p.description }}</p>
                                </div>
                                <div class="prompt-actions">
                                    <button @click="startEditing(p)" class="btn-secondary action-btn">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.pencil"></svg>
                                        Edit
                                    </button>
                                    <button @click="handleDelete(p.id)" class="btn-danger action-btn">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.trash_2"></svg>
                                        Delete
                                    </button>
                                </div>
                            </div>
                            <div v-else class="prompt-edit">
                                <input v-model="editData.name" placeholder="Name" class="text-input" />
                                <textarea v-model="editData.content" placeholder="Prompt content..." class="text-area"></textarea>
                                <input v-model="editData.description" placeholder="Description (optional)" class="text-input" />
                                <div class="prompt-actions">
                                    <button @click="handleUpdate" class="btn-primary action-btn">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.save"></svg>
                                        Save
                                    </button>
                                    <button @click="cancelEdit" class="btn-ghost action-btn">
                                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { toRef } from 'vue';
import { usePromptStore } from '@/chat/stores/prompt';
import { usePromptLibrary } from './usePromptLibrary';
import { ICONS } from '@/icons';

const props = defineProps<{ isVisible: boolean }>();
const emit = defineEmits<{ (e: 'close'): void }>();

const promptStore = usePromptStore();
const isVisibleRef = toRef(props, 'isVisible');

const { 
    newPrompt, 
    editingId, 
    editData, 
    handleCreate, 
    startEditing, 
    cancelEdit, 
    handleUpdate, 
    handleDelete 
} = usePromptLibrary(isVisibleRef);
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    color: var(--text-primary);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-default);
}

.modal-header h2 {
    margin: 0;
    font-size: 18px;
}

.close-btn {
    font-size: 20px;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.create-form, .prompt-list-container {
    margin-bottom: 24px;
}

.create-form h3, .prompt-list-container h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--text-secondary);
}

.text-input, .text-area {
    width: 100%;
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 8px;
    font-family: inherit;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;
    margin-bottom: 0; /* Was 8px, now handled by flex gap */
}

.text-input:focus, .text-area:focus {
    border-color: var(--accent-blue);
}

.text-area {
    resize: vertical;
    min-height: 60px;
}

.create-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
}

.prompt-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.prompt-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 12px;
    margin-bottom: 8px;
}

.prompt-view {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.prompt-edit {
    display: flex;
    flex-direction: column;
    gap: 8px; /* Replaces the margin-bottom on inputs for cleaner vertical spacing */
}
.prompt-info {
    flex: 1;
}

.prompt-info strong {
    font-size: 14px;
}

.role-tag {
    font-size: 11px;
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: var(--radius-sm);
    margin-left: 8px;
    color: var(--text-secondary);
}

.prompt-desc {
    margin: 4px 0 0 0;
    font-size: 12px;
    color: var(--text-muted);
}

.prompt-actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}

.action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
</style>