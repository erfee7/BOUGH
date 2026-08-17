import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSystemStore = defineStore('system', () => {
    const version = ref<string>('unknown');
    const isLoaded = ref(false);

    async function fetchVersion() {
        if (isLoaded.value) return;
        try {
            // /api/health is public, so native fetch is fine and avoids apiFetch import cycles
            const res = await fetch('/api/health');
            if (res.ok) {
                const data = await res.json();
                version.value = data.version || 'unknown';
            }
        } catch {
            // Silent fail, remains 'unknown'
        } finally {
            isLoaded.value = true;
        }
    }

    return { version, isLoaded, fetchVersion };
});