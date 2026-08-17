<template>
    <div class="welcome-overlay">
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
.welcome-overlay {
    position: absolute;
    inset: 0;                /* Full region below the config bar, including behind the composer */
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;    /* Never blocks the composer, even where it spans behind it */
}

.welcome-content {
    pointer-events: auto;    /* Re-enables interaction for the selector itself */
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