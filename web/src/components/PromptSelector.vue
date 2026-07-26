<template>
    <div class="prompt-selector">
        <div class="selector-header">
            <select v-model="selectedMode" @change="onSelectChange" class="prompt-select">
                <option value="none">No Prompt</option>
                <option value="custom">Custom</option>
                <option v-for="p in filteredPrompts" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <button @click="emit('openLibrary')" class="manage-btn" title="Manage Prompts">⚙️</button>
        </div>
        
        <!-- Only show textarea if Custom is selected -->
        <textarea 
            v-if="selectedMode === 'custom'"
            :value="modelValue" 
            @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
            class="prompt-textarea"
            placeholder="Write a custom prompt..."
        ></textarea>
        
        <!-- Show read-only preview if a preset is selected -->
        <div v-else-if="selectedMode !== 'none'" class="prompt-preview">
            {{ modelValue }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { usePrompts } from '../composables/usePrompts';
import { Prompt } from '../types';

const props = defineProps<{ 
    role: 'system' | 'developer', 
    modelValue: string 
}>();
const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'openLibrary'): void 
}>();

const { prompts, fetchPrompts } = usePrompts();

onMounted(() => {
    fetchPrompts(props.role);
});

const filteredPrompts = computed(() => {
    return prompts.value.filter((p: Prompt) => p.role === props.role);
});

const selectedMode = ref<string>('none');

// If parent clears the modelValue (e.g. after send), reset to 'none'
watch(() => props.modelValue, (newVal) => {
    if (!newVal && selectedMode.value !== 'custom') {
        selectedMode.value = 'none';
    }
});

function onSelectChange() {
    if (selectedMode.value === 'none') {
        emit('update:modelValue', '');
    } else if (selectedMode.value === 'custom') {
        // Emit empty string to let user start typing fresh
        emit('update:modelValue', '');
    } else {
        const selected = filteredPrompts.value.find(p => p.id === selectedMode.value);
        if (selected) {
            emit('update:modelValue', selected.content);
        }
    }
}
</script>

<style scoped>
.prompt-selector {
    margin-bottom: 12px;
    background: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 8px;
}

.selector-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.prompt-select {
    flex: 1;
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px;
    font-size: 13px;
    outline: none;
}

.manage-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #94a3b8;
    padding: 4px;
    transition: color 0.2s;
}

.manage-btn:hover {
    color: #f8fafc;
}

.prompt-textarea {
    width: 100%;
    background: transparent;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    font-family: inherit;
    font-size: 13px;
    resize: vertical;
    min-height: 60px;
    max-height: 120px;
    outline: none;
    box-sizing: border-box;
}

.prompt-textarea:focus {
    border-color: #3b82f6;
}

.prompt-preview {
    width: 100%;
    background: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    min-height: 60px;
    max-height: 120px;
    overflow-y: auto;
    white-space: pre-wrap;
    box-sizing: border-box;
}
</style>