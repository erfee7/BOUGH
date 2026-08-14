<template>
    <RouterView />
    <!-- Global Auth Modals -->
    <ChangePasswordModal v-if="authStore.isChangePasswordModalVisible" />
</template>

<script setup lang="ts">
import { useAuthStore } from '@/auth/stores/auth';
import ChangePasswordModal from '@/auth/ChangePasswordModal.vue';

const authStore = useAuthStore();
</script>