<template>
  <div class="contest-registration-container">
    <div class="registration-form">
      <h1 class="contest-title">🌹 Sorteo San Valentín 2025 💕</h1>
      <h2 class="prize-description">¡Gana una estadía romántica de 2 noches para una pareja!</h2>
      
      <div v-if="showSuccessMessage" class="success-message">
        <h3>¡Gracias por registrarte!</h3>
        <p>Revisa tu correo para verificar tu cuenta.</p>
      </div>

      <form v-else @submit.prevent="handleRegistration" class="registration-form-content">
        <h3>Inscríbete al concurso</h3>
        
        <div class="form-group">
          <label for="firstName">Nombre:</label>
          <input
            id="firstName"
            v-model="form.firstName"
            type="text"
            placeholder="Tu nombre"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="lastName">Apellido:</label>
          <input
            id="lastName"
            v-model="form.lastName"
            type="text"
            placeholder="Tu apellido"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="email">Correo Electrónico:</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="tu@email.com"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="phone">Teléfono:</label>
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            placeholder="123-456-7890"
            required
            :disabled="isLoading"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button 
          type="submit" 
          class="register-btn"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Registrando...' : 'Inscribirme al Sorteo' }}
        </button>
      </form>

      <div class="admin-link">
        <router-link to="/admin/login">¿Eres administrador? Inicia sesión aquí</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: ''
})

const isLoading = ref(false)
const errorMessage = ref('')
const showSuccessMessage = ref(false)

onMounted(() => {
  // Limpiar cualquier estado previo
  showSuccessMessage.value = false
  errorMessage.value = ''
})

const handleRegistration = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('http://localhost:8000/api/contest/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: form.value.firstName,
        last_name: form.value.lastName,
        email: form.value.email,
        phone: form.value.phone
      })
    })

    const data = await response.json()

    if (response.ok && data.success) {
      showSuccessMessage.value = true
      // Limpiar el formulario
      form.value = {
        firstName: '',
        lastName: '',
        email: '',
        phone: ''
      }
    } else {
      // Manejar errores específicos
      if (data.message) {
        errorMessage.value = data.message
      } else {
        errorMessage.value = 'Error al registrarse. Inténtalo de nuevo.'
      }
    }
  } catch (error) {
    console.error('Error de red:', error)
    errorMessage.value = 'Error de conexión. Por favor, inténtalo de nuevo.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.contest-registration-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b, #ff8e9b, #ffd93d);
  padding: 2rem;
}

.registration-form {
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
  margin-bottom: 1rem;
  color: #e91e63;
  font-weight: bold;
}

.prize-description {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  color: #666;
  font-weight: 500;
}

.registration-form-content h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
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

.success-message {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 1rem;
}

.success-message h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.success-message p {
  margin: 0;
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

.register-btn {
  width: 100%;
  background: linear-gradient(135deg, #e91e63, #ad1457);
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

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(233, 30, 99, 0.4);
}

.register-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.admin-link {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.admin-link a {
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
}

.admin-link a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .contest-registration-container {
    padding: 1rem;
  }
  
  .registration-form {
    padding: 2rem;
  }
  
  .contest-title {
    font-size: 2rem;
  }
  
  .prize-description {
    font-size: 1rem;
  }
}
</style>