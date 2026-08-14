import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUiStore = defineStore('ui', () => {
    const isSettingsModalVisible = ref(false);

    function openSettings() {
        isSettingsModalVisible.value = true;
    }

    function closeSettings() {
        isSettingsModalVisible.value = false;
    }

    return { isSettingsModalVisible, openSettings, closeSettings };
});