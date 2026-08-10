import { defineStore } from 'pinia';
import { ref } from 'vue';
import { Prompt } from '@/types';

export const usePromptStore = defineStore('prompt', () => {
    const prompts = ref<Prompt[]>([]);
    const isLoading = ref(false);
    const isInitialized = ref(false);

    async function fetchPrompts(force: boolean = false) {
        // If we've already fetched and aren't forcing a refresh, do nothing.
        // This prevents redundant calls when PromptSelector components mount/unmount.
        if (isInitialized.value && !force) return;
        
        isLoading.value = true;
        try {
            const response = await fetch('/api/chat/prompts');
            if (!response.ok) throw new Error('Failed to fetch prompts');
            prompts.value = await response.json();
            isInitialized.value = true; // Mark as initialized only on success
        } catch (error) {
            console.error("Error fetching prompts:", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function createPrompt(data: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>) {
        try {
            const response = await fetch('/api/chat/prompts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create prompt');
            await fetchPrompts(true); // Force refresh to get the new list
        } catch (error) {
            console.error("Error creating prompt:", error);
        }
    }

    async function updatePrompt(id: string, data: Partial<Prompt>) {
        try {
            const response = await fetch(`/api/chat/prompts/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update prompt');
            await fetchPrompts(true); // Force refresh
        } catch (error) {
            console.error("Error updating prompt:", error);
        }
    }

    async function deletePrompt(id: string) {
        try {
            const response = await fetch(`/api/chat/prompts/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete prompt');
            await fetchPrompts(true); // Force refresh
        } catch (error) {
            console.error("Error deleting prompt:", error);
        }
    }

    return {
        prompts,
        isLoading,
        fetchPrompts,
        createPrompt,
        updatePrompt,
        deletePrompt
    };
});