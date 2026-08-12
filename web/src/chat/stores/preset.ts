import { defineStore } from 'pinia';
import { ref } from 'vue';
import { GenerationPreset } from '@/types';

export const usePresetStore = defineStore('preset', () => {
    const presets = ref<GenerationPreset[]>([]);
    const isLoading = ref(false);
    const isInitialized = ref(false);

    async function fetchPresets(force: boolean = false) {
        if (isInitialized.value && !force) return;
        
        isLoading.value = true;
        try {
            const response = await fetch('/api/chat/presets');
            if (!response.ok) throw new Error('Failed to fetch presets');
            presets.value = await response.json();
            isInitialized.value = true;
        } catch (error) {
            console.error("Error fetching presets:", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function createPreset(data: { name: string, model: string | null, parameters: Record<string, unknown> }): Promise<GenerationPreset | null> {
        try {
            const response = await fetch('/api/chat/presets', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create preset');
            
            // Capture the newly created preset returned by the backend
            const newPreset = await response.json() as GenerationPreset;
            await fetchPresets(true); // Refresh the list for the dropdown
            return newPreset;
        } catch (error) {
            console.error("Error creating preset:", error);
            return null;
        }
    }

    async function updatePreset(id: string, data: { name: string, model: string | null, parameters: Record<string, unknown> }) {
        try {
            const response = await fetch(`/api/chat/presets/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update preset');
            await fetchPresets(true); // Force refresh
        } catch (error) {
            console.error("Error updating preset:", error);
        }
    }

    async function deletePreset(id: string) {
        try {
            const response = await fetch(`/api/chat/presets/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete preset');
            await fetchPresets(true);
        } catch (error) {
            console.error("Error deleting preset:", error);
        }
    }

    return {
        presets,
        isLoading,
        fetchPresets,
        createPreset,
        updatePreset,
        deletePreset
    };
});