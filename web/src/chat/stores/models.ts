import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { ModelInfo } from '@/types';

export const useModelsStore = defineStore('models', () => {
    const models = ref<ModelInfo[]>([]);
    const isLoading = ref(false);
    const isInitialized = ref(false);

    async function fetchModels(force = false) {
        if (!force && isInitialized.value) return;
        if (isLoading.value) return; // Prevent concurrent fetches
        
        isLoading.value = true;
        try {
            const response = await fetch('/api/chat/models');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            // Explicitly construct typed objects at the API boundary
            models.value = data.map((m: any) => ({
                id: String(m.id),
                name: String(m.name)
            }));
            isInitialized.value = true;
        } catch (error) {
            console.error('Failed to fetch models:', error);
            // We do not set isInitialized on error so it can retry next time
        } finally {
            isLoading.value = false;
        }
    }

    // Getter function to look up a model's info by ID
    const getModelById = computed(() => {
        return (id: string) => models.value.find(m => m.id === id);
    });

    return {
        models,
        isLoading,
        isInitialized,
        fetchModels,
        getModelById
    };
});