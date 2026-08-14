<template>
    <div class="login-container">
        <form @submit.prevent="handleLogin" class="login-form">
            <h2>BOUGH</h2>
            <div class="form-group">
                <input 
                    v-model="username" 
                    type="text" 
                    placeholder="Username" 
                    required 
                    :disabled="isLoading"
                />
            </div>
            <div class="form-group">
                <input 
                    v-model="password" 
                    type="password" 
                    placeholder="Password" 
                    required 
                    :disabled="isLoading"
                />
            </div>
            <p v-if="error" class="error-msg">{{ error }}</p>
            <button type="submit" :disabled="isLoading">
                {{ isLoading ? 'Logging in...' : 'Login' }}
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from './stores/auth';

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
    gap: 16px;
    padding: 32px;
    background: var(--bg-secondary);
    border-radius: 8px;
    width: 320px;
}
.form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--bg-tertiary);
    color: var(--text-primary);
    box-sizing: border-box;
}
button {
    padding: 10px;
    background: var(--accent-blue);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
.error-msg {
    color: var(--accent-red);
    font-size: 14px;
    margin: 0;
}
</style>