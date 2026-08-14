import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { User } from '@/types';
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const isAuthenticated = computed(() => !!user.value);
    const isInitializing = ref(true);

    // Called on app startup (via router guard) to restore session from HttpOnly cookie
    async function initialize() {
        isInitializing.value = true;
        try {
            const response = await fetch('/api/auth/me');
            if (response.ok) {
                user.value = await response.json();
            } else {
                user.value = null;
            }
        } catch (error) {
            user.value = null;
        } finally {
            isInitializing.value = false;
        }
    }

    // Called by LoginView.vue
    async function login(username: string, password: string): Promise<{ success: boolean; error?: string }> {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            if (response.ok) {
                user.value = await response.json();
                await router.push('/');
                return { success: true };
            } else {
                const data = await response.json();
                return { success: false, error: data.detail || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error' };
        }
    }

    // Will be used later by the UserMenu GUI
    async function logout() {
        await fetch('/api/auth/logout', { method: 'POST' });
        user.value = null;
        await router.push('/login');
    }

    // Called by apiFetch wrapper when any API call returns 401
    function handleExpiredSession() {
        user.value = null;
        if (router.currentRoute.value.name !== 'login') {
            router.push('/login');
        }
    }

    async function changePassword(oldPassword: string, newPassword: string): Promise<{ success: boolean; error?: string }> {
        try {
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
            });
            
            if (response.ok) {
                return { success: true };
            } else {
                const data = await response.json();
                return { success: false, error: data.detail || 'Failed to change password' };
            }
        } catch (error) {
            return { success: false, error: 'Network error' };
        }
    }

    return {
        user,
        isAuthenticated,
        isInitializing,
        initialize,
        login,
        logout,
        handleExpiredSession,
        changePassword
    };
});