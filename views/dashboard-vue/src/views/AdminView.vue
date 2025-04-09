<!-- src/views/DashboardView.vue -->
<template>
  <div>
    <h1>Dashboard</h1>
    <p v-if="isInitialized && isAuthenticated">Welcome, {{ userInfo?.preferred_username }}!</p>
    <p v-else-if="isInitialized">You need to log in to view the dashboard.</p>
    <p v-else>Loading user information...</p>
    <!-- Dashboard content goes here -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, inject } from 'vue';
import type { Ref } from 'vue';
import type Keycloak from 'keycloak-js';
import type { KeycloakProfile } from 'keycloak-js'; // Import specific types

// Inject Keycloak instance and initialization status
const keycloak = inject<Keycloak>('keycloak');
const isKeycloakInitialized = inject<Ref<boolean>>('isKeycloakInitialized');

const isAuthenticated = ref<boolean>(false);
const isInitialized = ref<boolean>(false);
const userInfo = ref<KeycloakProfile | null>(null); // Use KeycloakProfile type

onMounted(async () => {
  // Check initialization status from injected ref
  if (isKeycloakInitialized?.value) {
      isInitialized.value = true;
      if (keycloak?.authenticated) {
          isAuthenticated.value = true;
          try {
              // Load user profile if authenticated
              const profile = await keycloak.loadUserProfile();
              userInfo.value = profile;
               console.log("User Profile:", profile);
               console.log("Token Parsed:", keycloak.tokenParsed); // Access claims
          } catch (error) {
              console.error("Failed to load user profile:", error);
          }
      }
  } else {
       console.log("Dashboard mounted but Keycloak not yet initialized.");
       // You might want to add a watcher on isKeycloakInitialized if needed
  }
});

</script>