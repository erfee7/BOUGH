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
                    <!-- Future tabs will go here -->
                </nav>

                <!-- Right Content Area -->
                <div class="settings-pane">
                    <div v-if="activeTab === 'account'" class="account-section">
                        <div class="user-info">
                            <div class="user-avatar">👤</div>
                            <div class="user-details">
                                <span class="label">Signed in as</span>
                                <span class="username">{{ username }}</span>
                            </div>
                        </div>
                        
                        <div class="action-list">
                            <button class="action-btn" @click="isChangePasswordVisible = true">
                                Change Password
                            </button>
                            <button class="action-btn danger" @click="emit('logout')">
                                Logout
                            </button>
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
import { ref } from 'vue';
import ChangePasswordModal from './ChangePasswordModal.vue';

const props = defineProps<{ username: string }>();
const emit = defineEmits(['close', 'logout']);

const activeTab = ref<'account'>('account');
const isChangePasswordVisible = ref(false);
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
    border-radius: 12px;
    width: 640px;
    max-width: 90vw;
    height: 480px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    overflow: hidden;
}
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;
}
.modal-header h2 {
    margin: 0;
    font-size: 20px;
}
.close-btn {
    background: transparent;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--text-secondary);
    padding: 0 4px;
}
.close-btn:hover {
    color: var(--text-primary);
}

.settings-body {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.settings-nav {
    width: 180px;
    border-right: 1px solid var(--border-color);
    padding: 12px 8px;
    flex-shrink: 0;
    background: var(--bg-primary);
}
.nav-item {
    display: block;
    width: 100%;
    text-align: left;
    padding: 10px 12px;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 6px;
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

.user-info {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-color);
}
.user-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--bg-tertiary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.user-details {
    display: flex;
    flex-direction: column;
}
.user-details .label {
    font-size: 12px;
    color: var(--text-secondary);
}
.user-details .username {
    font-size: 16px;
    font-weight: 500;
}

.action-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.action-btn {
    text-align: left;
    padding: 10px 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.15s;
}
.action-btn:hover {
    background: var(--bg-primary);
}
.action-btn.danger {
    color: var(--accent-red, #e34c4c);
}
</style>