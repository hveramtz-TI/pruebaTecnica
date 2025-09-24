<template>
  <div class="winner-selection-container">
    <div class="winner-header">
      <h2>🏆 Sorteo de Ganador - San Valentín 2025</h2>
      <p>Selecciona aleatoriamente un ganador entre todos los participantes elegibles</p>
    </div>

    <!-- Estado: Botón de sorteo -->
    <div v-if="!winner && !loading" class="selection-section">
      <div class="stats-info">
        <div class="stat-card">
          <div class="stat-number">{{ eligibleCount }}</div>
          <div class="stat-label">Participantes Elegibles</div>
        </div>
      </div>

      <div class="selection-actions">
        <button 
          @click="confirmSelection" 
          class="select-winner-btn"
          :disabled="eligibleCount === 0"
        >
          🎲 Seleccionar Ganador Aleatorio
        </button>
        
        <p v-if="eligibleCount === 0" class="no-participants">
          ⚠️ No hay participantes elegibles para el sorteo
        </p>
      </div>
    </div>

    <!-- Estado: Cargando con animación -->
    <div v-if="loading" class="loading-section">
      <div class="loading-animation">
        <div class="spinner"></div>
        <div class="loading-text">
          <h3>🎰 Seleccionando ganador...</h3>
          <p>{{ loadingMessage }}</p>
        </div>
      </div>
    </div>

    <!-- Estado: Ganador seleccionado -->
    <div v-if="winner && !loading" class="winner-section">
      <div class="celebration-animation">
        <div class="confetti">🎊</div>
        <div class="confetti">🎉</div>
        <div class="confetti">✨</div>
        <div class="confetti">🏆</div>
      </div>

      <div class="winner-card">
        <div class="winner-header-card">
          <h2>🎉 ¡Felicidades! 🎉</h2>
          <h3>Ganador del Sorteo San Valentín 2025</h3>
        </div>

        <div class="winner-info">
          <div class="winner-details">
            <div class="detail-item">
              <span class="label">👤 Nombre:</span>
              <span class="value">{{ winner.name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">📧 Email:</span>
              <span class="value">{{ winner.email }}</span>
            </div>
            <div class="detail-item">
              <span class="label">📱 Teléfono:</span>
              <span class="value">{{ winner.phone }}</span>
            </div>
            <div class="detail-item">
              <span class="label">📅 Fecha de Registro:</span>
              <span class="value">{{ formatDate(winner.registration_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">🏆 Seleccionado:</span>
              <span class="value">{{ formatDate(winner.selected_at) }}</span>
            </div>
          </div>

          <div class="contest-info">
            <h4>📋 Información del Concurso</h4>
            <p><strong>Nombre:</strong> {{ winner.contest_name }}</p>
            <p><strong>Total de elegibles:</strong> {{ contest?.total_eligible || 'N/A' }}</p>
            <p><strong>Seleccionado por:</strong> {{ selectedBy?.admin_name }} ({{ selectedBy?.admin_email }})</p>
          </div>

          <div class="email-status">
            <p class="email-notification">
              📬 Se ha enviado un email de notificación al ganador automáticamente
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Errores -->
    <div v-if="error" class="error-section">
      <div class="error-message">
        ❌ {{ error }}
      </div>
    </div>

    <!-- Modal de confirmación -->
    <div v-if="showConfirmModal" class="modal-overlay" @click="cancelSelection">
      <div class="confirm-modal" @click.stop>
        <div class="modal-header">
          <h3>🎲 Confirmar Sorteo</h3>
        </div>
        <div class="modal-body">
          <p>¿Estás seguro de que quieres realizar el sorteo?</p>
          <p><strong>Participantes elegibles:</strong> {{ eligibleCount }}</p>
          <p><small>⚠️ Esta acción no se puede deshacer</small></p>
        </div>
        <div class="modal-actions">
          <button @click="cancelSelection" class="cancel-btn">
            Cancelar
          </button>
          <button @click="selectWinner" class="confirm-btn">
            🎯 Confirmar Sorteo
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// URL base de la API
const API_URL = 'http://127.0.0.1:8000/api'

// Interfaces
interface Winner {
  id: number
  name: string
  email: string
  phone: string
  registration_date: string
  selected_at: string
  contest_name: string
}

interface Contest {
  id: number
  name: string
  total_eligible: number
}

interface SelectedBy {
  admin_email: string
  admin_name: string
}

interface WinnerResponse {
  success: boolean
  message: string
  winner?: Winner
  contest?: Contest
  selected_by?: SelectedBy
}

// Estado del componente
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const winner = ref<Winner | null>(null)
const contest = ref<Contest | null>(null)
const selectedBy = ref<SelectedBy | null>(null)
const eligibleCount = ref(0)
const showConfirmModal = ref(false)
const loadingMessage = ref('')

// Mensajes de loading animados
const loadingMessages = [
  '🎰 Mezclando participantes...',
  '🍀 Buscando al afortunado...',
  '✨ Aplicando magia del sorteo...',
  '🎯 Seleccionando al ganador...',
  '🏆 ¡Casi listo!'
]

// Funciones
const fetchEligibleCount = async () => {
  try {
    if (!authStore.tokens?.access_token) {
      throw new Error('No hay token de autenticación')
    }

    const response = await axios.get(
      `${API_URL}/admin/participants/`,
      {
        headers: {
          'Authorization': `Bearer ${authStore.tokens.access_token}`
        }
      }
    )

    if (response.data.success) {
      eligibleCount.value = Number(response.data.eligible_count) || 0
    }
  } catch (err) {
    console.error('Error obteniendo count de elegibles:', err)
  }
}

const confirmSelection = () => {
  if (eligibleCount.value === 0) {
    error.value = 'No hay participantes elegibles para el sorteo'
    return
  }
  showConfirmModal.value = true
}

const cancelSelection = () => {
  showConfirmModal.value = false
}

const selectWinner = async () => {
  showConfirmModal.value = false
  loading.value = true
  error.value = ''
  
  // Animación de loading con mensajes
  let messageIndex: number = 0
  loadingMessage.value = loadingMessages[0]
  
  const messageInterval = setInterval(() => {
    messageIndex = (messageIndex + 1) % loadingMessages.length
    loadingMessage.value = loadingMessages[messageIndex]
  }, 800)

  try {
    if (!authStore.tokens?.access_token) {
      throw new Error('No hay token de autenticación')
    }

    // Simular un poco de suspenso
    await new Promise(resolve => setTimeout(resolve, 3000))

    const response = await axios.post<WinnerResponse>(
      `${API_URL}/admin/select-winner/`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${authStore.tokens.access_token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    clearInterval(messageInterval)

    if (response.data.success && response.data.winner) {
      winner.value = response.data.winner
      contest.value = response.data.contest || null
      selectedBy.value = response.data.selected_by || null
      
      // Actualizar el count de elegibles a 0 ya que se seleccionó ganador
      eligibleCount.value = 0
    } else {
      throw new Error(response.data.message || 'Error al seleccionar ganador')
    }
  } catch (err: unknown) {
    clearInterval(messageInterval)
    
    if (axios.isAxiosError(err)) {
      if (err.response?.status === 401) {
        error.value = 'Sesión expirada. Por favor, inicia sesión nuevamente.'
        authStore.logout()
      } else if (err.response?.data?.message) {
        error.value = err.response.data.message
        
        // Si ya hay un ganador, mostrar la información
        if (err.response.data.winner) {
          winner.value = err.response.data.winner
        }
      } else {
        error.value = 'Error de conexión al servidor'
      }
    } else {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido al seleccionar ganador'
      error.value = errorMessage
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

// Inicialización
onMounted(() => {
  fetchEligibleCount()
})
</script>

<style scoped>
.winner-selection-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.winner-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #e91e63, #ad1457);
  color: white;
  border-radius: 15px;
}

.winner-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.winner-header p {
  margin: 0;
  opacity: 0.9;
}

/* Sección de selección */
.selection-section {
  text-align: center;
}

.stats-info {
  margin-bottom: 2rem;
}

.stat-card {
  display: inline-block;
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 2px solid #4CAF50;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #4CAF50;
  margin: 0;
}

.stat-label {
  font-size: 1rem;
  color: #666;
  margin-top: 0.5rem;
}

.selection-actions {
  margin-top: 2rem;
}

.select-winner-btn {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.select-winner-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.select-winner-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.no-participants {
  color: #f44336;
  font-weight: 500;
  margin-top: 1rem;
}

/* Sección de loading */
.loading-section {
  text-align: center;
  padding: 3rem 2rem;
}

.loading-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text h3 {
  color: #4CAF50;
  margin: 0;
  font-size: 1.5rem;
}

.loading-text p {
  color: #666;
  margin: 0.5rem 0 0 0;
  font-size: 1.1rem;
}

/* Sección de ganador */
.winner-section {
  position: relative;
  text-align: center;
}

.celebration-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.confetti {
  position: absolute;
  font-size: 2rem;
  animation: fall 3s linear infinite;
}

.confetti:nth-child(1) {
  left: 10%;
  animation-delay: 0s;
}

.confetti:nth-child(2) {
  left: 30%;
  animation-delay: 0.5s;
}

.confetti:nth-child(3) {
  left: 70%;
  animation-delay: 1s;
}

.confetti:nth-child(4) {
  left: 90%;
  animation-delay: 1.5s;
}

@keyframes fall {
  0% {
    transform: translateY(-100px) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(calc(100vh + 100px)) rotate(360deg);
    opacity: 0;
  }
}

.winner-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 3px solid #FFD700;
  position: relative;
  z-index: 1;
}

.winner-header-card {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #8B4513;
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
}

.winner-header-card h2 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.winner-header-card h3 {
  margin: 0;
  font-size: 1.2rem;
}

.winner-info {
  display: grid;
  gap: 2rem;
}

.winner-details {
  text-align: left;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.label {
  font-weight: 600;
  color: #555;
  flex: 0 0 40%;
}

.value {
  color: #333;
  flex: 1;
  text-align: right;
}

.contest-info {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: left;
}

.contest-info h4 {
  margin: 0 0 1rem 0;
  color: #4CAF50;
}

.contest-info p {
  margin: 0.5rem 0;
}

.email-status {
  background: #e8f5e8;
  padding: 1rem;
  border-radius: 10px;
  border-left: 4px solid #4CAF50;
}

.email-notification {
  margin: 0;
  color: #2e7d2e;
  font-weight: 500;
}

/* Modal de confirmación */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirm-modal {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header h3 {
  margin: 0 0 1rem 0;
  color: #4CAF50;
}

.modal-body p {
  margin: 0.5rem 0;
  color: #555;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.cancel-btn, .confirm-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f44336;
  color: white;
}

.cancel-btn:hover {
  background: #d32f2f;
}

.confirm-btn {
  background: #4CAF50;
  color: white;
}

.confirm-btn:hover {
  background: #45a049;
}

/* Errores */
.error-section {
  margin-top: 2rem;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #f44336;
}

/* Responsive */
@media (max-width: 768px) {
  .winner-selection-container {
    padding: 1rem;
  }
  
  .winner-header {
    padding: 1rem;
  }
  
  .winner-header h2 {
    font-size: 1.5rem;
  }
  
  .select-winner-btn {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }
  
  .detail-item {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .value {
    text-align: left;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>