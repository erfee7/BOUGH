<template>
    <div class="menu-container" v-if="!isGenerating">
        <button @click.stop="toggleMenu" class="kebab-btn" :class="{ 'is-open': menuOpen }" title="More actions">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.vertical_dots"></svg>
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
                <button @click.stop="askForDeleteConfirm" class="menu-item danger">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.trash"></svg>
                    Delete
                </button>
            </template>
            
            <template v-else>
                <div class="confirm-box">
                    <span class="confirm-text">Delete this chat?</span>
                    <div class="confirm-actions">
                        <button @click.stop="cancelDelete" class="confirm-btn">Cancel</button>
                        <button @click.stop="confirmDelete" class="confirm-btn danger">Delete</button>
                    </div>
                </div>
            </template>
        </div>
    </div>
    <div v-else class="spinner"></div>
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
    background: none;
    border: none;
    cursor: pointer;
    color: inherit;
    opacity: 0;
    transition: opacity 0.15s, transform 0.15s;
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
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
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    z-index: 100;
    min-width: 160px;
    padding: 4px;
    margin-top: 4px;
    cursor: default;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: #cbd5e1;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    line-height: 1; /* Remove extra text spacing */
    transition: background-color 0.15s;
}

.menu-item svg {
    flex-shrink: 0; /* Prevent the icon from squishing */
}

.menu-item:hover {
    background: #334155;
    color: #f8fafc;
}

.menu-item.danger {
    color: #f87171;
}

.menu-item.danger:hover {
    background: rgba(239, 68, 68, 0.1);
}

.confirm-box {
    padding: 8px;
}

.confirm-text {
    display: block;
    font-size: 13px;
    color: #f8fafc;
    margin-bottom: 8px;
    white-space: nowrap;
}

.confirm-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}

.confirm-btn {
    background: #334155;
    border: none;
    color: #f8fafc;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: background-color 0.15s;
}

.confirm-btn:hover {
    background: #475569;
}

.confirm-btn.danger {
    background: #ef4444;
}

.confirm-btn.danger:hover {
    background: #dc2626;
}

.spinner {
    width: 16px;
    height: 16px;
    border: 2px solid #475569;
    border-top-color: #f8fafc;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>