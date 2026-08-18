<template>
    <div class="modal-backdrop" @click="emit('close')">
        <div class="modal-content" @click.stop>
            <div class="modal-header">
                <h2>Settings</h2>
                <button class="close-btn" @click="emit('close')">×</button>
            </div>
            
            <div class="settings-body">
                <!-- Left Tab Navigation -->
                <nav class="settings-nav">
                    <button 
                        :class="['nav-item', { active: activeTab === 'account' }]"
                        @click="activeTab = 'account'"
                    >
                        Account
                    </button>
                    <button 
                        :class="['nav-item', { active: activeTab === 'display' }]"
                        @click="activeTab = 'display'"
                    >
                        Display
                    </button>
                    <!-- Future tabs will go here -->

                    <span class="version-text">BOUGH {{ systemStore.version }}</span>
                </nav>

                <!-- Right Content Area -->
                <div class="settings-pane">
                    <div v-if="activeTab === 'account'" class="account-section">
                        <div class="section-header">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.user"></svg>
                            <h3 class="section-title">Account</h3>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Username</span>
                            <span class="detail-value">{{ username }}</span>
                        </div>
                        
                        <div class="action-list">
                            <button class="action-btn" @click="isChangePasswordVisible = true">
                                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.key_round"></svg>
                                Change Password
                            </button>
                            <button class="action-btn danger" @click="emit('logout')">
                                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.log_out"></svg>
                                Logout
                            </button>
                        </div>
                    </div>
                    <div v-if="activeTab === 'display'" class="display-section">
                        <div class="section-header">
                            <h3 class="section-title">Display</h3>
                        </div>
                        <div class="setting-row">
                            <div class="setting-info">
                                <label class="setting-label">Stream refresh interval</label>
                                <span class="setting-help">How often streamed tokens update on screen. 0 = every token.</span>
                            </div>
                            <div class="setting-control">
                                <input 
                                    type="range" 
                                    min="0" 
                                    max="1000" 
                                    step="1" 
                                    :value="props.streamRefreshInterval"
                                    @input="onIntervalInput(($event.target as HTMLInputElement).value)"
                                    class="interval-slider"
                                />
                                <input 
                                    type="number" 
                                    min="0" 
                                    max="1000" 
                                    step="1" 
                                    :value="props.streamRefreshInterval"
                                    @input="onIntervalInput(($event.target as HTMLInputElement).value)"
                                    class="interval-input"
                                />
                                <span class="unit">ms</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Locally managed Change Password Modal -->
        <ChangePasswordModal 
            v-if="isChangePasswordVisible" 
            @close="isChangePasswordVisible = false" 
        />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import ChangePasswordModal from './ChangePasswordModal.vue';
import { ICONS } from '@/icons';
import { useSystemStore } from '@/shared/stores/system';

const props = defineProps<{
    username: string;
    streamRefreshInterval: number;
}>();

const emit = defineEmits<{
    (e: 'close'): void;
    (e: 'logout'): void;
    (e: 'update:streamRefreshInterval', value: number): void;
}>();

const activeTab = ref<'account' | 'display'>('account');
const isChangePasswordVisible = ref(false);

const systemStore = useSystemStore();
onMounted(() => systemStore.fetchVersion());

function onIntervalInput(raw: string) {
    const trimmed = raw.trim();
    if (trimmed === '') return;          // User cleared the box: do nothing
    const n = Number(trimmed);
    if (Number.isNaN(n)) return;         // Not a number: ignore until valid
    const clamped = Math.min(1000, Math.max(0, Math.round(n)));
    emit('update:streamRefreshInterval', clamped);
}
</script>

<style scoped>
.modal-backdrop {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}
.modal-content {
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    width: 640px;
    max-width: 90vw;
    height: 480px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    overflow: hidden;
}
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-default);
    flex-shrink: 0;
}
.modal-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}
.close-btn {
    background: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 0 4px;
    display: flex;
    align-items: center;
}
.close-btn:hover {
    color: var(--text-primary);
}

.settings-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.version-text {
    margin-top: auto;
    padding: 8px 12px;
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
}

.settings-nav {
    width: 160px;
    border-right: 1px solid var(--border-default);
    padding: 12px 8px;
    flex-shrink: 0;
    background: var(--bg-primary);
    display: flex;
    flex-direction: column;
}
.nav-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 500;
    box-sizing: border-box;
}
.nav-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}
.nav-item.active {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.settings-pane {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
}

/* New Account Section Styles */
.section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-primary);
    margin-bottom: 24px;
}
.section-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.detail-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-default);
    margin-bottom: 24px;
}
.detail-label {
    font-size: 14px;
    color: var(--text-secondary);
}
.detail-value {
    font-size: 14px;
    color: var(--text-primary);
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace; /* Monospace for technical truth */
}

.action-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.action-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    text-align: left;
    padding: 10px 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    color: var(--text-primary);
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: 14px;
    transition: background 0.15s;
}
.action-btn:hover {
    background: var(--bg-primary);
}
.action-btn.danger {
    color: var(--accent-red, #e34c4c);
    border-color: transparent;
}
.action-btn.danger:hover {
    background: rgba(227, 76, 76, 0.1);
}

/* Display settings */
.setting-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 24px;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-default);
}
.setting-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
}
.setting-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
}
.setting-help {
    font-size: 12px;
    color: var(--text-secondary);
}
.setting-control {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}
.interval-slider {
    width: 180px;
    accent-color: var(--accent-blue);
}
.interval-input {
    width: 70px;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-sm);
    padding: 4px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    outline: none;
}
.interval-input:focus {
    border-color: var(--accent-blue);
}
.unit {
    font-size: 13px;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
}

@media (max-width: 768px) {
    .modal-content {
        position: relative; /* Anchor for the floating version text */
        max-height: 80dvh;
    }
    .settings-body {
        flex-direction: column;
    }
    .settings-nav {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border-default);
        flex-direction: row;
        align-items: center;
        padding: 8px 12px;
    }
    .nav-item {
        width: auto;
    }
    /* Out of the tab row's flow; pinned to the card corner instead */
    .version-text {
        position: absolute;
        right: 12px;
        bottom: 6px;
        margin: 0;
        padding: 0;
    }
    .settings-pane {
        padding: 16px 16px 28px; /* Extra bottom clears the floating version text */
    }
    .setting-row {
    flex-direction: column;
        gap: 12px;
    }
    .setting-control {
        width: 100%;
    }
    .interval-slider {
        flex: 1;
    }
}
</style>