<template>
    <div class="generation-config-bar">
        <!-- Sidebar Toggle (Mobile only) -->
        <button @click="emit('toggle-sidebar')" class="btn-icon menu-btn" title="Toggle sidebar">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.menu"></svg>
        </button>
        <!-- Preset Group (Always visible) -->
        <div class="config-group preset-group">
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
                <option v-if="generationConfigStore.loadedPresetId === 'custom'" value="custom" hidden>Custom</option>
                <option value="default">Default</option>
                <option v-for="p in presetStore.presets" :key="p.id" :value="p.id">
                    {{ p.name }}{{ generationConfigStore.loadedPresetId === p.id && generationConfigStore.isDirty ? ' *' : '' }}
                </option>
            </select>
            <button 
                :disabled="!generationConfigStore.isDirty || generationConfigStore.loadedPresetId === 'default' || generationConfigStore.loadedPresetId === 'custom'"
                @click="handleRevert" 
                class="btn-icon" 
                title="Revert to saved preset"
            >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.undo_2"></svg>
            </button>
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

        <!-- Toggle Button (Right next to preset group) -->
        <button @click="isExpanded = !isExpanded" class="btn-icon toggle-btn" :title="isExpanded ? 'Hide configs' : 'Show configs'">
            <!-- Single icon that rotates via CSS -->
            <svg class="toggle-icon" :class="{ 'expanded': isExpanded }" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
        </button>

        <!-- Expandable Section (Hidden by default) -->
        <div class="expandable-section" v-show="isExpanded">

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
        </div>

        <PresetModal 
            :isVisible="showPresetModal" 
            @close="showPresetModal = false" 
        />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useGenerationConfigStore } from '../stores/generationConfig';
import { usePresetStore } from '../stores/preset';
import { ICONS } from '@/icons';
import PresetModal from './PresetModal.vue';
import ModelSelector from './ModelSelector.vue';
import { loadLocalConfig } from '../persistence';

const generationConfigStore = useGenerationConfigStore();
const presetStore = usePresetStore();

const showPresetModal = ref(false);
const isExpanded = ref(false);

const emit = defineEmits<{
    (e: 'toggle-sidebar'): void
}>();

onMounted(async () => {
    await presetStore.fetchPresets();
    // Boot-apply the remembered preset pointer; unknown id or fetch failure -> default state
    const savedId = loadLocalConfig().presetId;
    const preset = savedId ? presetStore.presets.find(p => p.id === savedId) : undefined;
    if (preset) generationConfigStore.loadPreset(preset);
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

function handleRevert() {
    const id = generationConfigStore.loadedPresetId;
    if (id === 'default' || id === 'custom') return;
    
    const preset = presetStore.presets.find(p => p.id === id);
    if (preset) {
        // loadPreset automatically resets isDirty to false
        generationConfigStore.loadPreset(preset);
    }
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
    white-space: nowrap;
    flex-shrink: 0; /* Prevents the bar from being squashed by the message list */
}

.config-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}

.expandable-section {
    display: flex;
    align-items: center;
    gap: 20px;
    overflow-x: auto;
    flex: 1; /* Takes up remaining space if visible */
    min-width: 0;
    padding-right: 10px;
}

/* Hide scrollbar for Chrome, Safari and Opera */
.expandable-section::-webkit-scrollbar {
    display: none;
}
/* Hide scrollbar for IE, Edge and Firefox */
.expandable-section {
    -ms-overflow-style: none;
    scrollbar-width: none;
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
    flex-shrink: 0;
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

/* Toggle Button */
.toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Smooth rotation for the icon */
.toggle-icon {
    transition: transform 0.2s ease-in-out;
}

.toggle-icon.expanded {
    transform: rotate(180deg);
}

/* Hamburger: hidden on desktop, shown via the mobile block below */
.menu-btn {
    display: none;
}

@media (max-width: 768px) {
    .generation-config-bar {
        position: relative; /* Anchor for the dropdown panel */
        gap: 8px;
        padding: 8px 12px;
    }
    .preset-group {
        flex: 1;
        min-width: 0;
    }
    .preset-select {
        width: auto;
        min-width: 0;
        max-width: none;
        flex: 1;
    }
    .divider {
        display: none;
    }
    /* Expanded section becomes a stacked dropdown panel under the bar */
    .expandable-section {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        flex-direction: column;
        align-items: stretch;
        gap: 12px;
        padding: 12px;
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border-default);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        overflow: visible;
        z-index: 100;
    }
    .expandable-section .config-group {
        width: 100%;
    }
    .expandable-section .config-select {
        flex: 1;
    }
    .expandable-section .params-group {
        align-items: flex-start;
    }
    .expandable-section .params-container {
        flex-wrap: wrap;
        flex: 1;
        min-width: 0;
    }
    .menu-btn {
        display: flex;
    }

    .toggle-icon.expanded {
        transform: rotate(90deg); /* Panel expands downward on mobile */
    }
}
</style>