<!-- src/App.vue -->
<template>
  <div id="app-layout">
    <header>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link v-if="isAuthenticated" to="/dashboard">Dashboard</router-link>
        <span v-if="isAuthenticated"> | </span>
        <router-link v-if="canAccessAdmin" to="/admin">Admin</router-link>
         <span v-if="canAccessAdmin"> | </span>
        <button v-if="!isAuthenticated && isInitialized" @click="login">Login</button>
        <button v-if="isAuthenticated && isInitialized" @click="logout">Logout ({{ preferredUsername }})</button>
        <span v-if="!isInitialized">Loading...</span>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, watch, ref } from 'vue';
import type { Ref } from 'vue';
import type Keycloak from 'keycloak-js';
import router from './router'; // Import router for redirect after logout

// Inject Keycloak instance and initialization status
const keycloak = inject<Keycloak>('keycloak');
const isKeycloakInitialized = inject<Ref<boolean>>('isKeycloakInitialized');

// Local reactive refs to track auth state changes
const isAuthenticated = ref(keycloak?.authenticated ?? false);
const isInitialized = ref(isKeycloakInitialized?.value ?? false);
const preferredUsername = ref(keycloak?.tokenParsed?.preferred_username ?? '');
const userRoles = ref<string[]>(keycloak?.realmAccess?.roles ?? []);

// Watch for changes in the injected initialization status
watch(isKeycloakInitialized!, (newValue) => {
   console.log("App: Keycloak initialization status changed:", newValue);
   isInitialized.value = newValue;
   if (newValue && keycloak) {
        // Update local state once initialized
        isAuthenticated.value = keycloak.authenticated ?? false;
        preferredUsername.value = keycloak.tokenParsed?.preferred_username ?? '';
        userRoles.value = keycloak.realmAccess?.roles ?? [];
        console.log("App: Updated auth state:", { auth: isAuthenticated.value, user: preferredUsername.value, roles: userRoles.value });
   } else if (!newValue) {
       // Reset state if Keycloak fails to initialize or is reset
        isAuthenticated.value = false;
        preferredUsername.value = '';
        userRoles.value = [];
   }
}, { immediate: true }); // immediate: true runs the watcher once on component mount

// Computed property to check if user has admin role
const canAccessAdmin = computed(() => {
    return isAuthenticated.value && userRoles.value.includes('app_admin');
});

const login = () => {
  // Redirect to dashboard after login
  const redirectUri = window.location.origin + '/dashboard';
  keycloak?.login({ redirectUri });
};

const logout = () => {
  // Redirect to home page after logout
   const redirectUri = window.location.origin + '/';
  keycloak?.logout({ redirectUri });
};

</script>

<style scoped>
/* Add some basic styling */
#app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
header {
  background-color: #f0f0f0;
  padding: 1rem;
  border-bottom: 1px solid #ccc;
}
nav {
  display: flex;
  gap: 1rem;
  align-items: center;
}
main {
  flex-grow: 1;
  padding: 1rem;
}
button {
  padding: 0.3rem 0.8rem;
  cursor: pointer;
}
</style>