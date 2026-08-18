<template>
   <div class="menu-container">
        <div v-if="isGenerating" class="btn-icon kebab-btn is-generating" title="Generating title...">
            <span class="spinner"></span>
        </div>
        <template v-else>
            <button @click.stop="toggleMenu" class="btn-icon kebab-btn" :class="{ 'is-open': menuOpen }" title="More actions">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.ellipsis_vertical"></svg>
            </button>
        
            <div v-if="menuOpen" class="dropdown-menu">
                <template v-if="!confirmingDelete">
                    <button @click.stop="handleRename" class="menu-item">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.pencil"></svg>
                        Rename
                    </button>
                    <button @click.stop="handleGenerateTitle" class="menu-item">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.sparkles"></svg>
                        Auto Title
                    </button>
                    <button @click.stop="handleTouch" class="menu-item">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.chevrons_up"></svg>
                        Bump
                    </button>
                    <button @click.stop="askForDeleteConfirm" class="menu-item danger-text">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.trash_2"></svg>
                        Delete
                    </button>
                </template>
                <template v-else>
                    <div class="confirm-box">
                        <span class="confirm-text">Delete this chat?</span>
                        <div class="confirm-actions">
                            <button @click.stop="cancelDelete" class="btn-ghost confirm-btn-small">Cancel</button>
                            <button @click.stop="confirmDelete" class="btn-danger confirm-btn-small">Delete</button>
                        </div>
                    </div>
                </template>
            </div>
        </template>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { ICONS } from '@/icons';

const props = defineProps<{ 
    isGenerating: boolean 
}>();

const emit = defineEmits<{
    (e: 'rename'): void,
    (e: 'generate-title'): void,
    (e: 'touch'): void,
    (e: 'delete'): void
}>();

const menuOpen = ref(false);
const confirmingDelete = ref(false);

function toggleMenu() {
    menuOpen.value = !menuOpen.value;
    if (!menuOpen.value) {
        confirmingDelete.value = false; // Reset confirm state when closing
    }
}

function closeMenu() {
    menuOpen.value = false;
    confirmingDelete.value = false;
}

function handleRename() {
    closeMenu();
    emit('rename');
}

function handleGenerateTitle() {
    closeMenu();
    emit('generate-title');
}

function handleTouch() {
    closeMenu();
    emit('touch');
}

function askForDeleteConfirm() {
    confirmingDelete.value = true;
}

function cancelDelete() {
    confirmingDelete.value = false;
    closeMenu();
}

function confirmDelete() {
    closeMenu();
    emit('delete');
}

// Click outside to close
function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    // Simple check: if the click is not on a button/menu-item inside our container
    if (!target.closest('.menu-container')) {
        closeMenu();
    }
}

onMounted(() => {
    window.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
    window.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.menu-container {
    position: relative;
    display: flex;
    align-items: center;
}

.kebab-btn {
    opacity: 0;
    transition: opacity 0.15s, transform 0.15s;
}

.kebab-btn.is-open {
    opacity: 1;
}

.kebab-btn:hover {
    transform: scale(1.15);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    z-index: 100;
    min-width: 160px;
    padding: 4px;
    margin-top: 4px;
    cursor: default; /* Override inherited pointer */
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 14px;
    line-height: 1; /* Fix vertical alignment */
    transition: background-color 0.15s, color 0.15s;
}

.menu-item svg {
    flex-shrink: 0; /* Prevent icon squishing */
}

.menu-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.menu-item.danger-text {
    color: var(--accent-red);
}

.menu-item.danger-text:hover {
    background: rgba(239, 68, 68, 0.1);
}

.confirm-box {
    padding: 8px;
}

.confirm-text {
    display: block;
    font-size: 13px;
    color: var(--text-primary);
    margin-bottom: 8px;
    white-space: nowrap;
}

.confirm-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}

/* Smaller padding for inline confirmation buttons */
.confirm-btn-small {
    padding: 4px 8px;
    font-size: 12px;
}

/* Generating state: spinner occupies the kebab button's exact box,
   so the slot height is identical in both states by construction */
.kebab-btn.is-generating {
    opacity: 1; /* Always visible feedback, even without row hover */
    cursor: default;
}

.kebab-btn.is-generating:hover {
    background: none;
    border-color: transparent;
    color: var(--text-muted); /* Suppress the clickable-button hover look */
}

.kebab-btn.is-generating .spinner {
    box-sizing: border-box;
    width: 18px;  /* Same box as the 18px icon it replaces */
    height: 18px;
}
</style>