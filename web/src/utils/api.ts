import { useAuthStore } from '@/auth/stores/auth';
import router from '@/router';

/**
 * A wrapper around fetch that intercepts 401 Unauthorized responses.
 * If a 401 is detected, it clears the auth state and redirects to /login.
 */
export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const response = await fetch(input, init);
    
    if (response.status === 401) {
        const authStore = useAuthStore();
        authStore.handleExpiredSession();
        throw new Error('Session expired');
    }
    
    return response;
}