<template>
  <div class="participants-container">
    <div class="participants-header">
      <h2>Lista de Concursantes</h2>
      <div class="stats-summary">
        <div class="stat-card">
          <div class="stat-number">{{ totalCount }}</div>
          <div class="stat-label">Total</div>
        </div>
        <div class="stat-card verified">
          <div class="stat-number">{{ verifiedCount }}</div>
          <div class="stat-label">Verificados</div>
        </div>
        <div class="stat-card eligible">
          <div class="stat-number">{{ eligibleCount }}</div>
          <div class="stat-label">Elegibles</div>
        </div>
      </div>
    </div>

    <div class="participants-controls">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nombre o email..."
          class="search-input"
        />
      </div>
      <div class="filter-controls">
        <select v-model="statusFilter" class="status-filter">
          <option value="">Todos los estados</option>
          <option value="Completamente verificado">Completamente verificado</option>
          <option value="Email pendiente">Email pendiente</option>
          <option value="Contraseña pendiente">Contraseña pendiente</option>
          <option value="No elegible">No elegible</option>
        </select>
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-message">
      <p>Cargando lista de participantes...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="refreshData" class="retry-btn">Reintentar</button>
    </div>

    <div v-else-if="filteredParticipants.length === 0" class="no-data-message">
      <p>No se encontraron participantes que coincidan con los criterios de búsqueda.</p>
    </div>

    <div v-else class="participants-table-container">
      <table class="participants-table">
        <thead>
          <tr>
            <th @click="sortBy('name')" class="sortable">
              Nombre 
              <span v-if="sortField === 'name'" class="sort-indicator">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sortBy('email')" class="sortable">
              Email
              <span v-if="sortField === 'email'" class="sort-indicator">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Teléfono</th>
            <th @click="sortBy('verification_status')" class="sortable">
              Estado
              <span v-if="sortField === 'verification_status'" class="sort-indicator">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="sortBy('registration_date')" class="sortable">
              Fecha de Registro
              <span v-if="sortField === 'registration_date'" class="sort-indicator">
                {{ sortDirection === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="participant in paginatedParticipants" :key="participant.id">
            <td class="participant-name">{{ participant.name }}</td>
            <td class="participant-email">{{ participant.email }}</td>
            <td class="participant-phone">{{ participant.phone }}</td>
            <td class="participant-status">
              <span :class="['status-badge', getStatusClass(participant.verification_status)]">
                {{ participant.verification_status }}
              </span>
            </td>
            <td class="participant-date">
              {{ formatDate(participant.registration_date) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        @click="currentPage = 1" 
        :disabled="currentPage === 1"
        class="pagination-btn"
      >
        ≪
      </button>
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="pagination-btn"
      >
        ‹
      </button>
      
      <span class="pagination-info">
        Página {{ currentPage }} de {{ totalPages }} 
        ({{ filteredParticipants.length }} resultados)
      </span>
      
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="pagination-btn"
      >
        ›
      </button>
      <button 
        @click="currentPage = totalPages" 
        :disabled="currentPage === totalPages"
        class="pagination-btn"
      >
        ≫
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// URL base de la API
const API_URL = 'http://127.0.0.1:8000/api'

// Interfaces
interface Participant {
  id: number
  name: string
  email: string
  phone: string
  is_eligible: boolean
  is_email_verified: boolean
  has_password: boolean
  registration_date: string
  verification_status: string
}

interface ParticipantsResponse {
  success: boolean
  participants: Participant[]
  total_count: number
  verified_count: number
  eligible_count: number
}

// Estado del componente
const authStore = useAuthStore()
const loading = ref(false)
const error = ref('')
const participants = ref<Participant[]>([])

// Estadísticas
const totalCount = ref(0)
const verifiedCount = ref(0)
const eligibleCount = ref(0)

// Filtros y búsqueda
const searchQuery = ref('')
const statusFilter = ref('')

// Ordenamiento
const sortField = ref('registration_date')
const sortDirection = ref<'asc' | 'desc'>('desc')

// Paginación
const currentPage = ref(1)
const itemsPerPage = 10

// Computed properties
const filteredParticipants = computed(() => {
  let filtered = participants.value

  // Filtro de búsqueda
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(query) ||
      p.email.toLowerCase().includes(query)
    )
  }

  // Filtro de estado
  if (statusFilter.value) {
    filtered = filtered.filter(p => p.verification_status === statusFilter.value)
  }

  // Ordenamiento
  filtered.sort((a, b) => {
    let aValue = a[sortField.value as keyof Participant]
    let bValue = b[sortField.value as keyof Participant]

    if (typeof aValue === 'string') aValue = aValue.toLowerCase()
    if (typeof bValue === 'string') bValue = bValue.toLowerCase()

    if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
    if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredParticipants.value.length / itemsPerPage)
})

const paginatedParticipants = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredParticipants.value.slice(start, end)
})

// Métodos
const fetchParticipants = async () => {
  loading.value = true
  error.value = ''

  try {
    if (!authStore.tokens?.access_token) {
      throw new Error('No hay token de autenticación')
    }

    console.log('Token enviado:', authStore.tokens.access_token)
    console.log('Headers completos:', {
      'Authorization': `Bearer ${authStore.tokens.access_token}`
    })

    const response = await axios.get<ParticipantsResponse>(
      `${API_URL}/admin/participants/`, 
      {
        headers: {
          'Authorization': `Bearer ${authStore.tokens.access_token}`
        }
      }
    )

    if (response.data.success) {
      participants.value = response.data.participants
      totalCount.value = response.data.total_count
      verifiedCount.value = response.data.verified_count
      eligibleCount.value = response.data.eligible_count
    } else {
      throw new Error('Error en la respuesta del servidor')
    }
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 401) {
      error.value = 'Token de autenticación inválido o expirado'
      // Opcional: redirigir al login
      authStore.logout()
    } else {
      error.value = err instanceof Error ? err.message : 'Error al cargar la lista de participantes'
    }
    console.error('Error al obtener participantes:', err)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchParticipants()
}

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'Completamente verificado':
      return 'status-verified'
    case 'Email pendiente':
      return 'status-email-pending'
    case 'Contraseña pendiente':
      return 'status-password-pending'
    case 'No elegible':
      return 'status-not-eligible'
    default:
      return 'status-unknown'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  fetchParticipants()
})
</script>

<style scoped>
.participants-container {
  padding: 1rem;
}

.participants-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.participants-header h2 {
  margin: 0;
  color: #333;
}

.stats-summary {
  display: flex;
  gap: 1rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 80px;
}

.stat-card.verified {
  border-left: 4px solid #28a745;
}

.stat-card.eligible {
  border-left: 4px solid #007bff;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.participants-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-filter {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.875rem;
}

.refresh-btn, .retry-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.3s;
}

.refresh-btn:hover:not(:disabled), .retry-btn:hover {
  background-color: #0056b3;
}

.refresh-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.loading-message, .error-message, .no-data-message {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #dc3545;
}

.participants-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.participants-table {
  width: 100%;
  border-collapse: collapse;
}

.participants-table th,
.participants-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.participants-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.participants-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.3s;
}

.participants-table th.sortable:hover {
  background-color: #e9ecef;
}

.sort-indicator {
  margin-left: 0.5rem;
  color: #007bff;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-verified {
  background-color: #d4edda;
  color: #155724;
}

.status-email-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-password-pending {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-not-eligible {
  background-color: #f8d7da;
  color: #721c24;
}

.status-unknown {
  background-color: #e2e3e5;
  color: #383d41;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.pagination-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  min-width: 2.5rem;
  transition: background-color 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.pagination-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.pagination-info {
  margin: 0 1rem;
  font-size: 0.875rem;
  color: #666;
}

@media (max-width: 768px) {
  .participants-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-summary {
    width: 100%;
    justify-content: space-around;
  }

  .participants-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-controls {
    justify-content: space-between;
  }

  .participants-table {
    font-size: 0.875rem;
  }

  .participants-table th,
  .participants-table td {
    padding: 0.5rem;
  }
}
</style>