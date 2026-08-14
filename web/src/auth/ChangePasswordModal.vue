<template>
    <div class="modal-backdrop" @click="close">
        <div class="modal-content" @click.stop>
            <h2>Change Password</h2>
            <form @submit.prevent="handleSubmit" class="form-body">
                <div class="form-group">
                    <label>Current Password</label>
                    <input type="password" v-model="oldPassword" required :disabled="isLoading" />
                </div>
                <div class="form-group">
                    <label>New Password</label>
                    <input type="password" v-model="newPassword" required :disabled="isLoading" />
                </div>
                <div class="form-group">
                    <label>Confirm New Password</label>
                    <input type="password" v-model="confirmPassword" required :disabled="isLoading" />
                </div>
                
                <p v-if="localError" class="error-msg">{{ localError }}</p>
                
                <div class="modal-actions">
                    <button type="button" @click="close" class="btn-secondary" :disabled="isLoading">Cancel</button>
                    <button type="submit" class="btn-primary" :disabled="isLoading">
                        {{ isLoading ? 'Saving...' : 'Save Changes' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAuthStore } from '@/auth/stores/auth';

const authStore = useAuthStore();

const oldPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const isLoading = ref(false);
const localError = ref<string | null>(null);

// Reset form whenever the modal is opened
watch(() => authStore.isChangePasswordModalVisible, (isVisible) => {
    if (isVisible) {
        oldPassword.value = '';
        newPassword.value = '';
        confirmPassword.value = '';
        localError.value = null;
    }
});

function close() {
    if (!isLoading.value) {
        authStore.closeChangePasswordModal();
    }
}

async function handleSubmit() {
    localError.value = null;
    if (newPassword.value !== confirmPassword.value) {
        localError.value = "New passwords do not match.";
        return;
    }
    if (newPassword.value.length < 8) {
        localError.value = "Password must be at least 8 characters long.";
        return;
    }

    isLoading.value = true;
    const result = await authStore.changePassword(oldPassword.value, newPassword.value);
    
    if (!result.success) {
        localError.value = result.error || "Failed to change password.";
    }
    isLoading.value = false;
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
    border-radius: 12px;
    padding: 24px;
    width: 360px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
h2 {
    margin-top: 0;
    margin-bottom: 20px;
}
.form-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
}
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.form-group label {
    font-size: 14px;
    color: var(--text-secondary);
}
.form-group input {
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    box-sizing: border-box;
}
.error-msg {
    color: var(--accent-red, #e34c4c);
    font-size: 13px;
    margin: 0;
}
.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 8px;
}
button {
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    border: none;
    font-weight: 500;
}
.btn-secondary {
    background: transparent;
    color: var(--text-primary);
}
.btn-secondary:hover {
    background: var(--bg-tertiary);
}
.btn-primary {
    background: var(--accent-blue, #007bff);
    color: white;
}
.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
</style>