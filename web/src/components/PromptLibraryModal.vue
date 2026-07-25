<template>
    <div v-if="isVisible" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Prompt Library</h2>
                <button @click="emit('close')" class="close-btn">&times;</button>
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
                    <button @click="handleCreate" class="create-btn">Create</button>
                </div>

                <div class="prompt-list-container">
                    <h3>Saved Prompts</h3>
                    <ul class="prompt-list">
                        <li v-for="p in prompts" :key="p.id" class="prompt-item">
                            <div v-if="editingId !== p.id" class="prompt-view">
                                <div class="prompt-info">
                                    <strong>{{ p.name }}</strong> <span class="role-tag">{{ p.role }}</span>
                                    <p v-if="p.description" class="prompt-desc">{{ p.description }}</p>
                                </div>
                                <div class="prompt-actions">
                                    <button @click="startEditing(p)" class="action-btn edit">Edit</button>
                                    <button @click="handleDelete(p.id)" class="action-btn delete">Delete</button>
                                </div>
                            </div>
                            <div v-else class="prompt-edit">
                                <input v-model="editData.name" placeholder="Name" class="text-input" />
                                <textarea v-model="editData.content" placeholder="Prompt content..." class="text-area"></textarea>
                                <input v-model="editData.description" placeholder="Description (optional)" class="text-input" />
                                <div class="prompt-actions">
                                    <button @click="handleUpdate" class="action-btn save">Save</button>
                                    <button @click="cancelEdit" class="action-btn cancel">Cancel</button>
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
import { ref, watch } from 'vue';
import { usePrompts } from '../composables/usePrompts';
import { Prompt } from '../types';

const props = defineProps<{ isVisible: boolean }>();
const emit = defineEmits<{ (e: 'close'): void }>();

const { prompts, fetchPrompts, createPrompt, updatePrompt, deletePrompt } = usePrompts();

const newPrompt = ref({
    name: '',
    role: 'system' as 'system' | 'developer',
    content: '',
    description: ''
});

const editingId = ref<string | null>(null);
const editData = ref({
    name: '',
    content: '',
    description: ''
});

watch(() => props.isVisible, (visible) => {
    if (visible) {
        fetchPrompts();
    }
});

async function handleCreate() {
    if (!newPrompt.value.name || !newPrompt.value.content) return;
    await createPrompt(newPrompt.value);
    newPrompt.value = { name: '', role: 'system', content: '', description: '' };
}

function startEditing(p: Prompt) {
    editingId.value = p.id;
    editData.value = { name: p.name, content: p.content, description: p.description || '' };
}

function cancelEdit() {
    editingId.value = null;
}

async function handleUpdate() {
    if (!editingId.value) return;
    await updatePrompt(editingId.value, editData.value);
    editingId.value = null;
}

async function handleDelete(id: string) {
    await deletePrompt(id);
}
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
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    width: 100%;
    max-width: 600px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    color: #f8fafc;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #1e293b;
}

.modal-header h2 {
    margin: 0;
    font-size: 18px;
}

.close-btn {
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 24px;
    cursor: pointer;
    line-height: 1;
}

.close-btn:hover {
    color: #f8fafc;
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
    color: #cbd5e1;
}

.text-input, .text-area {
    width: 100%;
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    margin-bottom: 8px;
    font-family: inherit;
    font-size: 14px;
    outline: none;
    box-sizing: border-box;
}

.text-area {
    resize: vertical;
    min-height: 60px;
}

.create-btn {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
}

.create-btn:hover {
    background: #2563eb;
}

.prompt-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.prompt-item {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 8px;
}

.prompt-view {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.prompt-info {
    flex: 1;
}

.prompt-info strong {
    font-size: 14px;
}

.role-tag {
    font-size: 11px;
    background: #334155;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 8px;
    color: #cbd5e1;
}

.prompt-desc {
    margin: 4px 0 0 0;
    font-size: 12px;
    color: #94a3b8;
}

.prompt-actions {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
}

.action-btn {
    background: none;
    border: 1px solid #475569;
    color: #cbd5e1;
    border-radius: 6px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
}

.action-btn.edit:hover { border-color: #3b82f6; color: #3b82f6; }
.action-btn.delete:hover { border-color: #ef4444; color: #ef4444; }
.action-btn.save:hover { border-color: #22c55e; color: #22c55e; }
.action-btn.cancel:hover { border-color: #64748b; color: #64748b; }
</style>