<template>
  <main>
    <h1>BOUGH Web Skeleton</h1>
    <button @click="checkApi">Check API Health</button>
    <p v-if="apiStatus">API Status: {{ apiStatus }}</p>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const apiStatus = ref<string | null>(null)

async function checkApi() {
  try {
    // Notice the relative path - this hits Vite's proxy
    const response = await fetch('/api/health')
    const data = await response.json()
    apiStatus.value = data.status
  } catch (error) {
    apiStatus.value = 'Error connecting to API'
    console.error(error)
  }
}
</script>

<style scoped>
main {
  font-family: sans-serif;
  padding: 2rem;
}
button {
  padding: 0.5rem 1rem;
  cursor: pointer;
}
</style>