<template>
    <div class="welcome-container">
        <div class="welcome-content">
            <h2>Start a new chat</h2>
            <PromptSelector 
                role="system" 
                :modelValue="systemPrompt" 
                @update:modelValue="systemPrompt = $event"
                @openLibrary="emit('openLibrary')"
            />
        </div>
        <InputArea 
            :modelValue="inputText" 
            @update:modelValue="inputText = $event"
            :developerPrompt="developerPrompt"
            @update:developerPrompt="developerPrompt = $event"
            @send="send"
            @openLibrary="emit('openLibrary')"
            :isStreaming="isStreaming"
        />
    </div>
</template>

<script setup lang="ts">
import InputArea from './InputArea.vue';
import PromptSelector from './prompts/PromptSelector.vue';
import { useMessages } from './useMessages';
import { useChatEngine } from './useChatEngine';

const emit = defineEmits<{ 
    (e: 'openLibrary'): void
}>();

const {
    isStreaming
} = useMessages();

const { 
    inputText, 
    systemPrompt, 
    developerPrompt, 
    send 
} = useChatEngine();
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
    color: var(--text-primary);
}
</style>