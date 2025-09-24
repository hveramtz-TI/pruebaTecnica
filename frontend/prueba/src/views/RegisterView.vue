<template>
  <div class="register-container">
    <div class="register-form">
      <h2>Registro - Administrador</h2>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="firstName">Nombre:</label>
          <input
            id="firstName"
            v-model="form.firstName"
            type="text"
            placeholder="Juan"
            required
            :disabled="authStore.loading"
          />
        </div>

        <div class="form-group">
          <label for="lastName">Apellido:</label>
          <input
            id="lastName"
            v-model="form.lastName"
            type="text"
            placeholder="Pérez"
            required
            :disabled="authStore.loading"
          />
        </div>

        <div class="form-group">
          <label for="email">Email:</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="admin@ejemplo.com"
            required
            :disabled="authStore.loading"
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña:</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            required
            minlength="6"
            :disabled="authStore.loading"
          />
          <small class="password-hint">Mínimo 6 caracteres</small>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirmar Contraseña:</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            placeholder="••••••••"
            required
            minlength="6"
            :disabled="authStore.loading"
          />
        </div>

        <div v-if="passwordMismatch" class="error-message">
          Las contraseñas no coinciden
        </div>

        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <button 
          type="submit" 
          class="register-btn"
          :disabled="authStore.loading || passwordMismatch"
        >
          {{ authStore.loading ? 'Registrando...' : 'Registrarse' }}
        </button>
      </form>

      <div class="login-link">
        <p>¿Ya tienes cuenta? <router-link to="/admin/login">Inicia sesión aquí</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const passwordMismatch = computed(() => {
  return form.value.password !== form.value.confirmPassword && 
         form.value.confirmPassword.length > 0
})

onMounted(() => {
  // Si ya está autenticado, redirigir al dashboard
  if (authStore.isAuthenticated) {
    router.push('/admin/dashboard')
  }
  
  // Limpiar errores previos
  authStore.clearError()
})

const handleRegister = async () => {
  if (passwordMismatch.value) {
    return
  }

  try {
    const success = await authStore.createAdmin({
      first_name: form.value.firstName,
      last_name: form.value.lastName,
      email: form.value.email,
      password: form.value.password,
      password_confirm: form.value.confirmPassword
    })

    if (success) {
      // Redirigir al dashboard del administrador
      router.push('/admin/dashboard')
    }
  } catch (error) {
    console.error('Error en registro:', error)
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.register-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #28a745;
  box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.25);
}

.form-group input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.password-hint {
  color: #6c757d;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #f5c6cb;
}

.register-btn {
  width: 100%;
  background-color: #28a745;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-btn:hover:not(:disabled) {
  background-color: #218838;
}

.register-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 1.5rem;
}

.login-link a {
  color: #007bff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>