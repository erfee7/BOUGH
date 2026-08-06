<template>
    <div class="message-footer">
        <div v-if="siblingInfo.count > 1" class="sibling-nav">
            <button @click="emit('switch-sibling', 'prev')" :disabled="siblingInfo.currentIndex === 0" title="Previous message" class="btn-icon nav-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_left"></svg>
            </button>
            <span>{{ siblingInfo.currentIndex + 1 }} / {{ siblingInfo.count }}</span>
            <button @click="emit('switch-sibling', 'next')" :disabled="siblingInfo.currentIndex === siblingInfo.count - 1" title="Next message" class="btn-icon nav-btn">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevron_right"></svg>
            </button>
        </div>
        
        <button @click="copyToClipboard" class="btn-icon" :title="isCopied ? 'Copied!' : 'Copy to clipboard'">
            <svg v-if="!isCopied" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.copy"></svg>
            <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.check"></svg>
        </button>

        <button @click="emit('start-edit')" class="btn-icon" title="Edit message" :disabled="!isInteractive || role === 'system'">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.pencil"></svg>
        </button>

        <button @click="emit('generate')" :disabled="!isInteractive" class="btn-icon" :title="role === 'user' ? 'Generate response' : 'Continue from here'">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.sparkles"></svg>
        </button>

        <button v-if="role === 'assistant'" @click="emit('inspect')" class="btn-icon" :class="{ 'active': isInspecting }" :title="isInspecting ? 'Hide metadata' : 'Inspect metadata'">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.info"></svg>
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
    content: string | null,
    source: string,
    isInspecting: boolean
}>();

const emit = defineEmits<{
    (e: 'switch-sibling', direction: 'prev' | 'next'): void,
    (e: 'start-edit'): void,
    (e: 'generate'): void,
    (e: 'inspect'): void
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
    color: var(--text-muted);
    margin-right: 1px;
}

.sibling-nav span {
    min-width: 24px;
    text-align: center;
}

.nav-btn {
    font-size: 18px;
    line-height: 1;
}

.btn-icon.active {
    background: var(--bg-tertiary);
    color: var(--accent-blue);
    border-color: var(--accent-blue);
}
</style>