// src/main.ts
import { createApp, ref } from 'vue'; // Import ref
import App from './App.vue';
import router from './router'; // Assuming you have router configured
import { initKeycloak, keycloak } from './services/keycloak'; // Import the init function and instance
import './assets/main.css'; // Or your main CSS file

// Create a reactive ref to track initialization status
const isKeycloakInitialized = ref(false);

const app = createApp(App);

// Provide the Keycloak instance and initialization status to the app
app.provide('keycloak', keycloak);
app.provide('isKeycloakInitialized', isKeycloakInitialized);

app.use(router);

console.log("Starting Keycloak initialization...");

// Call initKeycloak and mount the app only after it's done
initKeycloak()
  .then((authenticated) => {
      console.log(`Keycloak initialized. Authenticated: ${authenticated}`);
      isKeycloakInitialized.value = true; // Update status
      app.mount('#app'); // Mount the app
  })
  .catch((error) => {
      console.error("Failed to initialize Keycloak, mounting app anyway or showing error state.", error);
      // Decide how to handle init failure: mount a limited app, show error message, etc.
      // For now, we'll still mount, but the flag indicates failure/pending state
      isKeycloakInitialized.value = false; // Ensure it's false on error
      app.mount('#app'); // Or maybe mount a specific error component
  });

// Optional: Make Keycloak instance globally available (alternative to provide/inject)
// app.config.globalProperties.$keycloak = keycloak;