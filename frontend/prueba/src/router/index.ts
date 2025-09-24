import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import ContestRegistration from '@/views/ContestRegistration.vue'
import EmailVerification from '@/views/EmailVerification.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/contest'
    },
    {
      path: '/contest',
      name: 'ContestRegistration',
      component: ContestRegistration,
      meta: { 
        public: true, // Ruta completamente pública
        title: 'Sorteo San Valentín 2025'
      }
    },
    {
      path: '/verify-email/:token',
      name: 'EmailVerification',
      component: EmailVerification,
      meta: { 
        public: true, // Ruta completamente pública
        title: 'Verificar Email - Sorteo San Valentín 2025'
      }
    },
    {
      path: '/admin/login',
      name: 'Login',
      component: LoginView,
      meta: { 
        requiresGuest: true, // Solo accesible si no está autenticado
        title: 'Iniciar Sesión - Admin'
      }
    },
    {
      path: '/admin/register',
      name: 'Register',
      component: RegisterView,
      meta: { 
        requiresGuest: true, // Solo accesible si no está autenticado
        title: 'Registro - Admin'
      }
    },
    {
      path: '/admin',
      redirect: '/admin/dashboard'
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { 
        requiresAuth: true, // Solo accesible si está autenticado
        title: 'Panel de Administrador'
      }
    }
  ],
})

// Guard de navegación para proteger rutas
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Inicializar la autenticación desde localStorage
  authStore.initAuth()
  
  // Actualizar el título de la página
  if (to.meta.title) {
    if (to.meta.public) {
      document.title = to.meta.title as string
    } else {
      document.title = `${to.meta.title} - Admin Panel`
    }
  }

  // Si es una ruta pública, permitir acceso sin restricciones
  if (to.meta.public) {
    next()
    return
  }

  // Verificar si la ruta requiere autenticación
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // Redirigir al login de admin si no está autenticado
    next('/admin/login')
    return
  }

  // Verificar si la ruta solo es para invitados (no autenticados)
  if (to.meta.requiresGuest && authStore.isLoggedIn) {
    // Redirigir al dashboard si ya está autenticado
    next('/admin/dashboard')
    return
  }

  // Permitir la navegación
  next()
})

export default router
