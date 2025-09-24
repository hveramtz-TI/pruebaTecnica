<template>
  <div class="verification-container">
    <div class="verification-form">
      <h1 class="contest-title">🌹 Sorteo San Valentín 2025 💕</h1>
      
      <!-- Loading state -->
      <div v-if="isLoadingToken" class="loading-message">
        <h3>Verificando enlace...</h3>
        <p>Por favor espera mientras verificamos tu enlace de registro.</p>
      </div>

      <!-- Token invalid -->
      <div v-else-if="!tokenValid" class="error-message">
        <h3>❌ Enlace inválido</h3>
        <p>{{ tokenError }}</p>
        <router-link to="/contest" class="back-button">
          ← Volver al registro
        </router-link>
      </div>

      <!-- Success message -->
      <div v-else-if="showSuccessMessage" class="success-message">
        <h3>¡Cuenta activada exitosamente! 🎉</h3>
        <p>Tu cuenta ha sido activada. Ya estás participando en el sorteo.</p>
        <router-link to="/contest" class="back-button">
          ← Volver al inicio
        </router-link>
      </div>

      <!-- Password creation form -->
      <div v-else class="password-form">
        <h3>Completa tu registro</h3>
        <p class="welcome-message">
          ¡Hola <strong>{{ userInfo.user_name }}</strong>! 
          Para completar tu participación en el sorteo, crea tu contraseña.
        </p>

        <form @submit.prevent="handlePasswordCreation">
          <div class="form-group">
            <label for="password">Nueva Contraseña:</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="••••••••"
              required
              minlength="8"
              :disabled="isLoading"
            />
            <small class="password-hint">Mínimo 8 caracteres</small>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirmar Contraseña:</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="••••••••"
              required
              minlength="8"
              :disabled="isLoading"
            />
          </div>

          <div v-if="passwordMismatch" class="error-message">
            Las contraseñas no coinciden
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <button 
            type="submit" 
            class="finish-btn"
            :disabled="isLoading || passwordMismatch || !passwordsValid"
          >
            {{ isLoading ? 'Activando cuenta...' : 'Terminar Registro' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const form = ref({
  password: '',
  confirmPassword: ''
})

const isLoadingToken = ref(true)
const isLoading = ref(false)
const tokenValid = ref(false)
const tokenError = ref('')
const errorMessage = ref('')
const showSuccessMessage = ref(false)
const userInfo = ref({
  user_name: '',
  user_email: ''
})

const passwordMismatch = computed(() => {
  return form.value.password !== form.value.confirmPassword && 
         form.value.confirmPassword.length > 0
})

const passwordsValid = computed(() => {
  return form.value.password.length >= 8 && 
         form.value.confirmPassword.length >= 8 && 
         !passwordMismatch.value
})

onMounted(async () => {
  const token = route.params.token as string
  
  if (!token) {
    tokenError.value = 'Token de verificación no proporcionado.'
    tokenValid.value = false
    isLoadingToken.value = false
    return
  }

  await verifyToken(token)
})

const verifyToken = async (token: string) => {
  try {
    const response = await fetch(`http://localhost:8000/api/verify-token/${token}/`)
    const data = await response.json()

    if (response.ok && data.valid) {
      tokenValid.value = true
      userInfo.value = {
        user_name: data.user_name,
        user_email: data.user_email
      }
    } else {
      tokenValid.value = false
      tokenError.value = data.message || 'Token de verificación inválido.'
    }
  } catch (error) {
    console.error('Error verificando token:', error)
    tokenValid.value = false
    tokenError.value = 'Error de conexión. Por favor, inténtalo de nuevo.'
  } finally {
    isLoadingToken.value = false
  }
}

const handlePasswordCreation = async () => {
  if (!passwordsValid.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const token = route.params.token as string
    
    const response = await fetch('http://localhost:8000/api/verify-email/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        password: form.value.password,
        password_confirm: form.value.confirmPassword
      })
    })

    const data = await response.json()

    if (response.ok && data.success) {
      showSuccessMessage.value = true
      // Limpiar formulario
      form.value = {
        password: '',
        confirmPassword: ''
      }
    } else {
      errorMessage.value = data.message || 'Error al crear la contraseña. Inténtalo de nuevo.'
    }
  } catch (error) {
    console.error('Error creando contraseña:', error)
    errorMessage.value = 'Error de conexión. Por favor, inténtalo de nuevo.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.verification-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b, #ff8e9b, #ffd93d);
  padding: 2rem;
}

.verification-form {
  background: white;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.contest-title {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #e91e63;
  font-weight: bold;
}

.loading-message {
  color: #666;
  padding: 2rem;
}

.loading-message h3 {
  color: #333;
  margin-bottom: 1rem;
}

.password-form h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.welcome-message {
  background: #f0f9ff;
  color: #0369a1;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  border-left: 4px solid #0284c7;
  text-align: left;
}

.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #e91e63;
  box-shadow: 0 0 0 3px rgba(233, 30, 99, 0.1);
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

.success-message {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 1rem;
}

.success-message h3 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
}

.success-message p {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  border: 1px solid #ffcdd2;
  font-weight: 500;
}

.finish-btn {
  width: 100%;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.finish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.finish-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.back-button {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .verification-container {
    padding: 1rem;
  }
  
  .verification-form {
    padding: 2rem;
  }
  
  .contest-title {
    font-size: 2rem;
  }
}
</style>