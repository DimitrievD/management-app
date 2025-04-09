// src/router/index.ts
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import { keycloak } from '@/services/keycloak'; // Import keycloak instance
import { shallowRef } from 'vue'; // Import shallowRef

// Use shallowRef for component imports if they might be large or cause reactivity issues
const DashboardView = shallowRef(() => import('../views/DashboardView.vue'));
const AccessDeniedView = shallowRef(() => import('../views/AccessDeniedView.vue')); // Create this view

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: false } // Public route
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['team_member', 'project_manager', 'app_admin'] } // Protected route, specify allowed roles
  },
  {
     path: '/admin', // Example admin route
     name: 'admin',
     component: () => import('../views/AdminView.vue'), // Lazy load admin view
     meta: { requiresAuth: true, roles: ['app_admin'] } // Only app_admin role
  },
  {
    path: '/access-denied',
    name: 'access-denied',
    component: AccessDeniedView,
    meta: { requiresAuth: false }
  },
  // Add other routes here
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// --- Navigation Guard ---
router.beforeEach(async (to, from, next) => {
    // Check if Keycloak instance is available and initialized (basic check)
     // A more robust check might involve the isKeycloakInitialized ref if passed down or managed globally
    if (!keycloak || !keycloak.authenticated === undefined) {
       // Keycloak might not be initialized yet, wait briefly or handle loading state
       // console.warn("Keycloak not ready, potentially redirecting or waiting...");
       // For simplicity now, let's assume it will be ready soon after app init
    }

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const requiredRoles = to.meta.roles as string[] | undefined; // Get roles from route meta

    if (requiresAuth) {
        if (!keycloak.authenticated) {
            // Not authenticated, redirect to Keycloak login
            console.log("Not authenticated, redirecting to login...");
            const loginUrl = keycloak.createLoginUrl({
                redirectUri: window.location.origin + to.fullPath // Redirect back to intended page after login
            });
            window.location.href = loginUrl; // Redirect
            // Alternatively, use keycloak.login() if you don't need to specify redirectUri dynamically like this
            // keycloak.login({ redirectUri: window.location.origin + to.fullPath });
            // next(false); // Prevent navigation
        } else {
            // Authenticated, check roles if required
            if (requiredRoles && requiredRoles.length > 0) {
                const hasRole = requiredRoles.some(role => keycloak.hasRealmRole(role));
                if (hasRole) {
                    console.log("User authenticated and has required role(s).");
                    next(); // User has required role, proceed
                } else {
                    console.log("User authenticated but lacks required role(s). Redirecting to Access Denied.");
                    next({ name: 'access-denied' }); // Redirect to an 'Access Denied' page
                }
            } else {
                console.log("User authenticated, no specific roles required.");
                next(); // Route requires auth but no specific roles, proceed
            }
        }
    } else {
        // Route does not require authentication
        console.log("Route does not require authentication.");
        next(); // Proceed
    }
});


export default router;