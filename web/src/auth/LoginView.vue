<template>
    <div class="login-container">
        <form @submit.prevent="handleLogin" class="login-form">
            <div class="login-header">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="ICONS.user"></svg>
                <h2>BOUGH</h2>
            </div>
            
            <div class="form-group">
                <label for="username">Username</label>
                <input 
                    id="username"
                    v-model="username" 
                    type="text" 
                    required 
                    :disabled="isLoading"
                    autocomplete="username"
                />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input 
                    id="password"
                    v-model="password" 
                    type="password" 
                    required 
                    :disabled="isLoading"
                    autocomplete="current-password"
                />
            </div>
            
            <p v-if="error" class="error-msg">{{ error }}</p>
            
            <button type="submit" class="login-btn" :disabled="isLoading">
                {{ isLoading ? 'Connecting...' : 'Enter' }}
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from './stores/auth';
import { ICONS } from '@/icons';

const authStore = useAuthStore();
const username = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref<string | null>(null);

async function handleLogin() {
    isLoading.value = true;
    error.value = null;
    
    const result = await authStore.login(username.value, password.value);
    
    if (!result.success) {
        error.value = result.error || 'Invalid credentials';
    }
    
    isLoading.value = false;
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: var(--bg-primary);
}
.login-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 40px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-default);
    border-radius: 12px;
    width: 100%;
    max-width: 360px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.login-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    color: var(--text-primary);
}
.login-header h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 1px;
}
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.form-group label {
    font-size: 13px;
    color: var(--text-secondary);
    font-weight: 500;
}
.form-group input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    background: var(--bg-tertiary);
    color: var(--text-primary);
    font-size: 14px;
    box-sizing: border-box;
    font-family: inherit;
}
.form-group input:focus {
    outline: none;
    border-color: var(--accent-blue);
}
.login-btn {
    padding: 12px;
    background: var(--accent-blue);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: opacity 0.15s;
}
.login-btn:hover {
    opacity: 0.9;
}
.login-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}
.error-msg {
    color: var(--accent-red, #e34c4c);
    font-size: 13px;
    margin: 0;
    text-align: center;
}
</style>