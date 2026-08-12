<template>
    <div class="generation-config-bar">
        <!-- Preset Group -->
        <div class="config-group">
            <select 
                :value="generationConfigStore.loadedPresetId" 
                @change="handlePresetChange" 
                class="preset-select"
                :class="{
                    'is-preset': generationConfigStore.loadedPresetId !== 'default' && generationConfigStore.loadedPresetId !== 'custom',
                    'is-default': generationConfigStore.loadedPresetId === 'default',
                    'is-dirty': generationConfigStore.loadedPresetId === 'custom' || generationConfigStore.isDirty
                }"
            >
                <!-- Hidden option for binding the dirty state, never shown in the dropdown list -->
                <option v-if="generationConfigStore.loadedPresetId === 'custom'" value="custom" hidden>Custom</option>
                <option value="default">Default</option>
                <option v-for="p in presetStore.presets" :key="p.id" :value="p.id">
                    {{ p.name }}{{ generationConfigStore.loadedPresetId === p.id && generationConfigStore.isDirty ? ' *' : '' }}
                </option>
            </select>
            <button 
                :disabled="generationConfigStore.loadedPresetId === 'default' || generationConfigStore.loadedPresetId === 'custom'" 
                @click="handleUpdate" 
                class="btn-icon" 
                title="Update current preset"
            >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.save"></svg>
            </button>
            <button @click="showPresetModal = true" class="btn-icon" title="Save As / Manage Presets">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.settings"></svg>
            </button>
        </div>

        <div class="divider"></div>

        <!-- Model Group -->
        <div class="config-group">
            <label class="config-label">Model</label>
            <ModelSelector />
        </div>
        
        <!-- Reasoning Group -->
        <div class="config-group">
            <label class="config-label">Reasoning</label>
            <select v-model="generationConfigStore.reasoningEffort" class="config-select">
                <option :value="null">Default</option>
                <option value="minimal">Minimal</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="xhigh">Extra High</option>
                <option value="max">Maximal</option>
            </select>
        </div>
        
        <!-- Params Group -->
        <div class="config-group params-group">
            <label class="config-label">Params</label>
            <div class="params-container">
                <div v-for="param in generationConfigStore.customParams" :key="param.id" class="param-chip">
                    <input type="text" v-model="param.key" placeholder="key" class="param-input key-input">
                    <span class="param-separator">:</span>
                    <input type="text" v-model="param.rawValue" placeholder="value" class="param-input value-input">
                    <button @click="generationConfigStore.removeParam(param.id)" class="param-remove-btn">
                        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.x"></svg>
                    </button>
                </div>
                <button @click="generationConfigStore.addParam" class="add-param-btn">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.plus"></svg>
                    Add
                </button>
            </div>
        </div>

        <PresetModal 
            :isVisible="showPresetModal" 
            @close="showPresetModal = false" 
        />
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useGenerationConfigStore } from '../stores/generationConfig';
import { usePresetStore } from '../stores/preset';
import { ICONS } from '@/icons';
import PresetModal from './PresetModal.vue';
import ModelSelector from './ModelSelector.vue';

const generationConfigStore = useGenerationConfigStore();
const presetStore = usePresetStore();

const showPresetModal = ref(false);

onMounted(() => {
    presetStore.fetchPresets();
    // Initialize to default if nothing is loaded
    if (!generationConfigStore.loadedPresetId) {
        generationConfigStore.loadedPresetId = 'default';
    }
});

function handlePresetChange(event: Event) {
    const value = (event.target as HTMLSelectElement).value;
    if (value === 'default') {
        generationConfigStore.clearConfig();
    } else if (value !== 'custom') {
        const preset = presetStore.presets.find(p => p.id === value);
        if (preset) {
            generationConfigStore.loadPreset(preset);
        }
    }
}

async function handleUpdate() {
    const id = generationConfigStore.loadedPresetId;
    if (!id || id === 'default' || id === 'custom') return;
    
    const existing = presetStore.presets.find(p => p.id === id);
    if (!existing) return;
    
    const data = generationConfigStore.buildPresetData(existing.name);
    await presetStore.updatePreset(id, data);
    
    // Mark as clean so the asterisk goes away
    generationConfigStore.isDirty = false; 
}
</script>

<style scoped>
.generation-config-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 12px 2%;
    border-bottom: 1px solid var(--border-default);
    background: var(--bg-primary);
    overflow-x: auto;
    white-space: nowrap;
    flex-shrink: 0; /* Prevents the bar from being squashed by the message list */
}

.config-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}

.config-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}

.config-input, .config-select {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 6px 10px;
    font-family: inherit;
    font-size: 13px;
    outline: none;
    cursor: pointer;
}

.config-input:focus, .config-select:focus {
    border-color: var(--accent-blue);
}

.config-input {
    width: 180px;
    cursor: text;
}

.config-select {
    overflow: hidden;
    text-overflow: ellipsis; /* Truncate long preset names with '...' */
    white-space: nowrap;
}

/* Preset Badge Styles */
.preset-select {
    width: 200px;
    min-width: 200px;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    
    /* Chunky Badge Base */
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    padding: 8px 12px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    outline: none;
    cursor: pointer;
    transition: border-color 0.2s, color 0.2s;
}

.preset-select:focus {
    border-color: var(--accent-blue);
}

/* State Colors */
.preset-select.is-preset {
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}

.preset-select.is-default {
    color: var(--text-muted);
}

.preset-select.is-dirty {
    color: var(--accent-yellow);
    border-color: var(--accent-yellow);
}

/* Divider Enhancements */
.divider {
    width: 2px; /* Thicker */
    height: 28px; /* Taller */
    background-color: var(--border-hover); /* Brighter */
    flex-shrink: 0;
    margin: 0 4px; /* Give it some breathing room */
}

.params-container {
    display: flex;
    align-items: center;
    gap: 8px;
}

.param-chip {
    display: flex;
    align-items: center;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 2px 4px 2px 8px;
    flex-shrink: 0; /* Prevent chips from squishing inside their container */
}

.param-input {
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-family: monospace;
    font-size: 12px;
    width: 60px;
    outline: none;
    padding: 4px 2px;
}

.key-input {
    font-weight: 600;
    color: var(--accent-blue);
}

.value-input {
    width: 80px;
}

.param-separator {
    color: var(--text-muted);
    margin: 0 2px;
}

.param-remove-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    border-radius: var(--radius-sm);
}

.param-remove-btn:hover {
    color: var(--accent-red);
    background: var(--bg-tertiary);
}

.add-param-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    background: transparent;
    border: 1px dashed var(--border-default);
    color: var(--text-muted);
    border-radius: var(--radius-sm);
    padding: 4px 10px;
    font-size: 12px;
    cursor: pointer;
    transition: border-color 0.2s, color 0.2s;
    flex-shrink: 0;
}

.add-param-btn:hover {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
}
</style>