import { ref } from 'vue';
import { Prompt } from '../../types';

const prompts = ref<Prompt[]>([]);
const isLoading = ref(false);

export function usePrompts() {
    
    async function fetchPrompts() {
        isLoading.value = true;
        try {
            const response = await fetch('/api/chat/prompts');
            if (!response.ok) throw new Error('Failed to fetch prompts');
            prompts.value = await response.json();
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
            await fetchPrompts(); // Refresh list
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
            await fetchPrompts(); // Refresh list
        } catch (error) {
            console.error("Error updating prompt:", error);
        }
    }

    async function deletePrompt(id: string) {
        try {
            const response = await fetch(`/api/chat/prompts/${id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Failed to delete prompt');
            await fetchPrompts(); // Refresh list
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
}