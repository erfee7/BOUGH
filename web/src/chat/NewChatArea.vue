<template>
    <div class="welcome-container">
        <div class="welcome-content">
            <h2>Start a new chat</h2>
            <PromptSelector 
                role="system" 
                :modelValue="systemPrompt" 
                @update:modelValue="emit('update:systemPrompt', $event)"
                @openLibrary="emit('openLibrary')"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import PromptSelector from './prompts/PromptSelector.vue';

defineProps<{ 
    systemPrompt: string 
}>();

const emit = defineEmits<{ 
    (e: 'update:systemPrompt', value: string): void,
    (e: 'openLibrary'): void
}>();
</script>

<style scoped>
.welcome-container {
    flex: 1;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.welcome-content {
    width: calc(90% - 48px); /* Matches input area responsive padding roughly */
    max-width: 800px;
    text-align: center;
    box-sizing: border-box;
}

.welcome-content h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: var(--text-primary);
}
</style>