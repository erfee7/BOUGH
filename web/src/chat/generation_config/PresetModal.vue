<template>
    <div v-if="isVisible" class="modal-overlay" @click.self="emit('close')">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Generation Presets</h2>
                <button @click="emit('close')" class="btn-icon close-btn" title="Close">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                </button>
            </div>
            
            <div class="modal-body">
                <div class="create-form">
                    <h3>Save Current Config</h3>
                    <input v-model="newPresetName" placeholder="Preset name" class="text-input" />
                    <button @click="handleCreate" class="btn-primary create-btn" :disabled="!newPresetName.trim()">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.save"></svg>
                        Save Current Config
                    </button>
                </div>

                <div class="preset-list-container">
                    <h3>Saved Presets</h3>
                    <ul class="preset-list">
                        <li v-for="p in presetStore.presets" :key="p.id" class="preset-item">
                            <div class="preset-info">
                                <strong>{{ p.name }}</strong>
                                <span class="preset-meta">{{ p.model || 'Server Default' }}</span>
                                <span class="preset-params" v-if="Object.keys(p.parameters).length > 0">
                                    {{ JSON.stringify(p.parameters) }}
                                </span>
                            </div>
                            <div class="preset-actions">
                                <button @click="handleLoad(p)" class="btn-secondary action-btn">
                                    Load
                                </button>
                                <button @click="handleDelete(p.id)" class="btn-danger action-btn">
                                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.trash_2"></svg>
                                </button>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { usePresetStore } from '../stores/preset';
import { useGenerationConfigStore } from '../stores/generationConfig';
import { GenerationPreset } from '@/types';
import { ICONS } from '@/icons';

defineProps<{ isVisible: boolean }>();
const emit = defineEmits<{ (e: 'close'): void }>();

const presetStore = usePresetStore();
const generationConfigStore = useGenerationConfigStore();

const newPresetName = ref('');

async function handleCreate() {
    if (!newPresetName.value.trim()) return;
    const data = generationConfigStore.buildPresetData(newPresetName.value);
    const newPreset = await presetStore.createPreset(data);
    
    if (newPreset) {
        // Immediately load the new preset so the config bar reflects it as active & clean
        generationConfigStore.loadPreset(newPreset);
        newPresetName.value = '';
        emit('close');
    }
}

function handleLoad(preset: GenerationPreset) {
    generationConfigStore.loadPreset(preset);
    emit('close');
}

async function handleDelete(id: string) {
    await presetStore.deletePreset(id);
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

.modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.create-form, .preset-list-container {
    margin-bottom: 24px;
}

.create-form h3, .preset-list-container h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--text-secondary);
}

.text-input {
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
    margin-bottom: 8px;
}

.text-input:focus {
    border-color: var(--accent-blue);
}

.create-btn {
    display: flex;
    align-items: center;
    gap: 6px;
}

.preset-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.preset-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 12px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.preset-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.preset-info strong {
    font-size: 14px;
}

.preset-meta {
    font-size: 12px;
    color: var(--text-muted);
    font-family: monospace;
}

.preset-params {
    font-size: 11px;
    color: var(--text-faded);
    font-family: monospace;
    background: var(--bg-primary);
    padding: 4px 6px;
    border-radius: var(--radius-sm);
    max-width: 350px;
    overflow-x: auto;
    white-space: nowrap;
}

.preset-actions {
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

@media (max-width: 768px) {
    .modal-content {
        width: calc(100% - 32px);
        max-height: calc(100dvh - 64px);
    }
}
</style>