<template>
    <div class="generation-config-bar">
        <div class="config-group">
            <label class="config-label">Model</label>
            <input 
                type="text" 
                v-model="generationConfigStore.model" 
                placeholder="Server default" 
                class="config-input"
            />
        </div>
        
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
</template>

<script setup lang="ts">
import { useGenerationConfigStore } from '../stores/generationConfig';
import { ICONS } from '@/icons';

const generationConfigStore = useGenerationConfigStore();
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
}

.add-param-btn:hover {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
}
</style>