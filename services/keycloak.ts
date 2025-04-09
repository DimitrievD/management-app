// src/services/keycloak.ts
import Keycloak from 'keycloak-js';

// Configuration details matching your Keycloak setup
const keycloakConfig: Keycloak.KeycloakConfig = {
    url: 'http://localhost:8080/auth', // Base URL of Keycloak server (adjust if needed later for Docker)
    realm: 'task-app-realm',         // Your realm name
    clientId: 'vue-dashboard'         // Your client ID for this frontend
};

// Initialize Keycloak instance
const keycloak = new Keycloak(keycloakConfig);

// Function to initialize Keycloak and handle authentication
// Returns a promise that resolves when Keycloak is initialized (or fails)
const initKeycloak = (): Promise<boolean> => {
    return new Promise((resolve, reject) => {
        console.log("Initializing Keycloak...");
        keycloak.init({
            onLoad: 'check-sso', // Can be 'login-required' or 'check-sso'
                                // 'check-sso': Checks if user is already logged in (in background)
                                // 'login-required': Requires user to be logged in
            silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html', // Optional: For silent check SSO
            pkceMethod: 'S256' // Recommended for public clients
         })
            .then((authenticated) => {
                if (authenticated) {
                    console.log("User is authenticated");
                    // Set interval to update token periodically
                    setInterval(() => {
                        keycloak.updateToken(70) // Update token if expires within 70 seconds
                            .then(refreshed => {
                                if (refreshed) {
                                    console.log('Token refreshed' + refreshed);
                                } else {
                                    // console.log('Token not refreshed, valid for '
                                    //     + Math.round(keycloak.tokenParsed.exp + keycloak.timeSkew - new Date().getTime() / 1000) + ' seconds');
                                }
                            }).catch(() => {
                                console.error('Failed to refresh token');
                                keycloak.logout(); // Optionally logout if refresh fails
                            });
                    }, 60000); // Check every 60 seconds
                } else {
                    console.log("User is not authenticated");
                }
                resolve(authenticated); // Resolve the promise with authentication status
            })
            .catch((error) => {
                console.error("Keycloak initialization failed:", error);
                // Handle initialization error (e.g., Keycloak server down)
                // You might want to display an error message to the user
                reject(error); // Reject the promise on error
            });
    });
};

// Optional: Create silent check SSO HTML file if using 'check-sso'
// Create public/silent-check-sso.html with simple content:
/*
<!DOCTYPE html>
<html>
<head><title>Keycloak Silent Check SSO</title></head>
<body>
  <script>
    parent.postMessage(location.href, location.origin);
  </script>
</body>
</html>
*/

export { keycloak, initKeycloak };