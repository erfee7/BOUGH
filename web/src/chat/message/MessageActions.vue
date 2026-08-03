<template>
    <div class="message-footer">
        <div v-if="siblingInfo.count > 1" class="sibling-nav">
            <button @click="emit('switch-sibling', 'prev')" :disabled="siblingInfo.currentIndex === 0" title="Previous message" class="action-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_left"></svg>
            </button>
            <span>{{ siblingInfo.currentIndex + 1 }} / {{ siblingInfo.count }}</span>
            <button @click="emit('switch-sibling', 'next')" :disabled="siblingInfo.currentIndex === siblingInfo.count - 1" title="Next message" class="action-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
            </button>
        </div>
        
        <button @click="copyToClipboard" class="action-btn" :title="isCopied ? 'Copied!' : 'Copy to clipboard'">
            <svg v-if="!isCopied" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.copy"></svg>
            <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.check"></svg>
        </button>

        <button @click="emit('start-edit')" class="action-btn" title="Edit message" :disabled="!isInteractive">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.pencil"></svg>
        </button>
        <button @click="emit('generate')" :disabled="!isInteractive" class="action-btn" :title="role === 'user' ? 'Generate response' : 'Continue from here'">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.sparkles"></svg>
        </button>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ICONS } from '@/icons';

const props = defineProps<{ 
    siblingInfo: { count: number, currentIndex: number },
    isInteractive: boolean,
    role: string,
    content: string | null
}>();

const emit = defineEmits<{
    (e: 'switch-sibling', direction: 'prev' | 'next'): void,
    (e: 'start-edit'): void,
    (e: 'generate'): void
}>();

const isCopied = ref(false);

async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(props.content || '');
        isCopied.value = true;
        setTimeout(() => {
            isCopied.value = false;
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}
</script>

<style scoped>
.message-footer {
    margin-top: 12px;
    display: flex;
    align-items: center;
    gap: 1px;
    opacity: 0.4;
    transition: opacity 0.2s;
}

.message-tile:hover .message-footer {
    opacity: 1;
}

.sibling-nav {
    display: flex;
    align-items: center;
    gap: 1px;
    font-size: 14px;
    color: #94a3b8;
    margin-right: 1px;
}

.sibling-nav span {
    min-width: 24px;
    text-align: center;
}

.sibling-nav button {
    background: none;
    border: 1px solid transparent;
    color: #94a3b8;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    line-height: 1;
}

.sibling-nav button:hover {
    color: #f8fafc;
    background: #1e293b;
    border-color: #334155;
}

.sibling-nav button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.action-btn {
    background: none;
    border: 1px solid transparent;
    color: #94a3b8;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.action-btn:hover {
    color: #f8fafc;
    background: #1e293b;
    border-color: #334155;
}

.action-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}
</style>