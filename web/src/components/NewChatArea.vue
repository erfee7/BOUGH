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
        <InputArea 
            :modelValue="modelValue" 
            @update:modelValue="emit('update:modelValue', $event)"
            :developerPrompt="developerPrompt"
            @update:developerPrompt="emit('update:developerPrompt', $event)"
            @send="emit('send')"
            @openLibrary="emit('openLibrary')"
            :isStreaming="isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import InputArea from './InputArea.vue';
import PromptSelector from './PromptSelector.vue';

const props = defineProps<{ 
    modelValue: string, 
    isStreaming: boolean,
    systemPrompt: string,
    developerPrompt: string 
}>();

const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'update:systemPrompt', value: string): void,
    (e: 'update:developerPrompt', value: string): void,
    (e: 'send'): void,
    (e: 'openLibrary'): void
}>();
</script>

<style scoped>
.welcome-container {
    position: relative;
    height: 100%;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-end; /* Keeps InputArea at the bottom */
}

.welcome-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: calc(90% - 48px); /* Matches input area responsive padding roughly */
    max-width: 800px;
    text-align: center;
    box-sizing: border-box;
}

.welcome-content h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: #f8fafc;
}
</style>