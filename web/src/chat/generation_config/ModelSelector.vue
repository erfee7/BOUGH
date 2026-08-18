<template>
    <div class="model-selector-wrapper" ref="wrapperRef">
        <button 
            class="model-trigger" 
            @click="togglePopover"
            :title="generationConfigStore.model || 'Server default'"
        >
            <span class="model-trigger-text">
                {{ generationConfigStore.model || 'Server default' }}
            </span>
        </button>

        <Teleport to="body">
            <div v-if="isPopoverOpen" class="model-popover" :style="popoverStyle" ref="popoverRef">
                <div class="model-search-row">
                    <input 
                        type="text" 
                        v-model="searchQuery" 
                        placeholder="Search by ID..." 
                        class="model-search-input"
                        ref="searchInputRef"
                    />
                    <button 
                        @click="handleRefresh" 
                        class="btn-icon"
                        :class="{ 'is-spinning': modelsStore.isLoading }"
                        :disabled="modelsStore.isLoading"
                        title="Force refresh model list"
                    >
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.rotate_cw"></svg>
                    </button>
                </div>
                
                <div class="model-list">
                    <div 
                        class="model-item" 
                        :class="{ 'is-selected': generationConfigStore.model === '' }"
                        @click="selectModel('')"
                        title="Server default"
                    >
                        Server default
                    </div>
                    <div 
                        v-for="m in filteredModels" 
                        :key="m.id" 
                        class="model-item" 
                        :class="{ 'is-selected': generationConfigStore.model === m.id }"
                        @click="selectModel(m.id)"
                        :title="m.name"
                    >
                        {{ m.id }}
                    </div>
                    <div v-if="filteredModels.length === 0 && !modelsStore.isLoading" class="model-empty">
                        No models found.
                    </div>
                    <div v-if="modelsStore.isLoading && modelsStore.models.length === 0" class="model-empty">
                        Loading models...
                    </div>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue';
import { useGenerationConfigStore } from '../stores/generationConfig';
import { useModelsStore } from '../stores/models';
import { ICONS } from '@/icons';

const generationConfigStore = useGenerationConfigStore();
const modelsStore = useModelsStore();

const isPopoverOpen = ref(false);
const searchQuery = ref('');
const wrapperRef = ref<HTMLElement | null>(null);
const popoverRef = ref<HTMLElement | null>(null);
const searchInputRef = ref<HTMLInputElement | null>(null);
const popoverStyle = ref<Record<string, string>>({});

const filteredModels = computed(() => {
    const query = searchQuery.value.toLowerCase().trim();
    if (!query) return modelsStore.models;
    return modelsStore.models.filter(m => m.id.toLowerCase().includes(query));
});

function togglePopover() {
    isPopoverOpen.value = !isPopoverOpen.value;
    if (isPopoverOpen.value) {
        if (!modelsStore.isInitialized && !modelsStore.isLoading) {
            modelsStore.fetchModels();
        }
        nextTick(() => {
            if (wrapperRef.value) {
                const rect = wrapperRef.value.getBoundingClientRect();
                popoverStyle.value = {
                    top: `${rect.bottom + 4}px`,
                    left: `${rect.left}px`,
                    // Give the popover a minimum width so the search box isn't cramped
                    width: `${Math.max(rect.width, 360)}px`
                };
            }
            searchInputRef.value?.focus();
        });
    } else {
        searchQuery.value = '';
    }
}

function selectModel(id: string) {
    generationConfigStore.model = id;
    isPopoverOpen.value = false;
    searchQuery.value = '';
}

async function handleRefresh() {
    // Guard against multiple clicks
    if (modelsStore.isLoading) return;
    await modelsStore.fetchModels(true);
}

function handleClickOutside(event: MouseEvent) {
    const target = event.target as Node;
    const clickedInsideWrapper = wrapperRef.value && wrapperRef.value.contains(target);
    const clickedInsidePopover = popoverRef.value && popoverRef.value.contains(target);
    
    if (!clickedInsideWrapper && !clickedInsidePopover) {
        isPopoverOpen.value = false;
        searchQuery.value = '';
    }
}

watch(isPopoverOpen, (isOpen) => {
    if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside);
    } else {
        document.removeEventListener('mousedown', handleClickOutside);
    }
});

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<style scoped>
.model-selector-wrapper {
    position: relative;
    display: inline-block;
}

.model-trigger {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 6px 10px;
    font-family: monospace;
    font-size: 13px;
    outline: none;
    cursor: pointer;
    width: 180px;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.model-trigger:hover {
    border-color: var(--accent-blue);
}

/* Popover styles (Teleported to body) */
.model-popover {
    position: absolute;
    z-index: 1000; /* Ensure it sits above everything */
    background: var(--bg-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.model-search-row {
    display: flex;
    align-items: center;
    padding: 8px;
    border-bottom: 1px solid var(--border-default);
    gap: 8px;
}

.model-search-input {
    flex: 1;
    box-sizing: border-box; /* Ensure padding/border doesn't expand it beyond flex bounds */
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 6px 10px;
    font-family: monospace;
    font-size: 13px;
    outline: none;
}

.model-search-input:focus {
    border-color: var(--accent-blue);
}

.btn-icon.is-spinning svg {
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.model-list {
    max-height: 300px;
    overflow-y: auto;
    padding: 4px 0;
}

.model-item {
    padding: 8px 12px;
    font-family: monospace;
    font-size: 13px;
    color: var(--text-primary);
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.model-item:hover {
    background: var(--bg-secondary);
}

.model-item.is-selected {
    background: var(--bg-tertiary);
    color: var(--accent-blue);
    font-weight: 600;
}

.model-empty {
    padding: 12px;
    font-size: 13px;
    color: var(--text-muted);
    text-align: center;
}

@media (max-width: 768px) {
    .model-selector-wrapper {
        display: block;
        flex: 1;
        min-width: 0;
    }
    .model-trigger {
        width: 100%;
    }
}
</style>