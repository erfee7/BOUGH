<template>
    <div class="settings-wrapper" ref="wrapperRef">
        <button class="settings-trigger" @click="togglePopover">
            <span class="user-icon">👤</span>
            <span class="username">{{ username }}</span>
            <span class="chevron" :class="{ open: isPopoverOpen }">⌃</span>
        </button>

        <Teleport to="body">
            <div v-if="isPopoverOpen" class="settings-popover" ref="popoverRef" :style="popoverStyle" @click.stop>
                <div class="popover-header">
                    Signed in as
                    <strong>{{ username }}</strong>
                </div>
                <div class="popover-actions">
                    <button class="popover-item" @click="emit('openChangePassword')">
                        Change Password
                    </button>
                    <button class="popover-item logout" @click="emit('logout')">
                        Logout
                    </button>
                </div>
            </div>
        </Teleport>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps<{ username: string }>();
const emit = defineEmits(['logout', 'openChangePassword']);

const wrapperRef = ref<HTMLElement | null>(null);
const popoverRef = ref<HTMLElement | null>(null);
const isPopoverOpen = ref(false);
const popoverStyle = ref<Record<string, string>>({});

function calculatePosition() {
    if (!wrapperRef.value) return;
    const rect = wrapperRef.value.getBoundingClientRect();
    popoverStyle.value = {
        position: 'fixed',
        bottom: `${window.innerHeight - rect.top + 8}px`,
        left: `${rect.left}px`,
        zIndex: '9999'
    };
}

function togglePopover() {
    if (!isPopoverOpen.value) calculatePosition();
    isPopoverOpen.value = !isPopoverOpen.value;
}

function handleClickOutside(event: MouseEvent) {
    const target = event.target as Node;
    if (
        isPopoverOpen.value &&
        wrapperRef.value && !wrapperRef.value.contains(target) &&
        popoverRef.value && !popoverRef.value.contains(target)
    ) {
        isPopoverOpen.value = false;
    }
}

watch(isPopoverOpen, (isOpen) => {
    if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside);
    } else {
        document.removeEventListener('mousedown', handleClickOutside);
    }
});

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<style scoped>
.settings-wrapper {
    width: 100%;
}
.settings-trigger {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    border-radius: 6px;
    box-sizing: border-box;
}
.settings-trigger:hover {
    background: var(--bg-tertiary);
}
.user-icon {
    font-size: 16px;
}
.username {
    flex: 1;
    text-align: left;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.chevron {
    transition: transform 0.2s;
}
.chevron.open {
    transform: rotate(180deg);
}

/* Teleported Popover Styles */
.settings-popover {
    width: 220px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    overflow: hidden;
}
.popover-header {
    padding: 12px 16px;
    font-size: 12px;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-color);
}
.popover-header strong {
    display: block;
    font-size: 14px;
    color: var(--text-primary);
    margin-top: 2px;
    overflow: hidden;
    text-overflow: ellipsis;
}
.popover-actions {
    padding: 4px;
}
.popover-item {
    width: 100%;
    text-align: left;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}
.popover-item:hover {
    background: var(--bg-tertiary);
}
.popover-item.logout {
    color: var(--accent-red, #e34c4c);
}
</style>