import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/auth/stores/auth';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'login',
            // Login view is isolated in shared/
            component: () => import('@/auth/LoginView.vue')
        },
        {
            path: '/',
            name: 'chat',
            // Chat layout is isolated in chat/
            component: () => import('@/chat/ChatLayout.vue')
        }
    ]
});

// Global guard: waits for auth to initialize before allowing access
router.beforeEach(async (to) => {
    const authStore = useAuthStore();
    
    if (authStore.isInitializing) {
        await authStore.initialize();
    }

    if (!authStore.isAuthenticated && to.name !== 'login') {
        return { name: 'login' };
    }
    
    if (authStore.isAuthenticated && to.name === 'login') {
        return { name: 'chat' };
    }
});

export default router;