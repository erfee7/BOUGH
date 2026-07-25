<template>
    <div class="welcome-container">
        <div class="welcome-content">
            <h2>Start a new chat</h2>
            <InputArea 
                :modelValue="modelValue" 
                @update:modelValue="emit('update:modelValue', $event)"
                @send="emit('send')"
                :isStreaming="isStreaming"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import InputArea from './InputArea.vue';

const props = defineProps<{ modelValue: string, isStreaming: boolean }>();
const emit = defineEmits<{ 
    (e: 'update:modelValue', value: string): void, 
    (e: 'send'): void 
}>();
</script>

<style scoped>
.welcome-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}
.welcome-content {
    width: 100%;
    max-width: 800px;
}
.welcome-content h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: #f8fafc;
    text-align: center;
}
</style>