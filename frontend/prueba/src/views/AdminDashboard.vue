<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="header-content">
        <h1>Panel de Administrador</h1>
        <div class="admin-info">
          <span>Bienvenido, {{ authStore.currentAdmin?.email }}</span>
          <button @click="handleLogout" class="logout-btn">
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <div class="dashboard-content">
        <div class="welcome-card">
          <h2>¡Bienvenido al Dashboard!</h2>
          <p>Esta es una ruta privada solo accesible para administradores autenticados.</p>
          
          <div class="admin-details">
            <h3>Información del Administrador:</h3>
            <div class="detail-item">
              <strong>ID:</strong> {{ authStore.currentAdmin?.id }}
            </div>
            <div class="detail-item">
              <strong>Email:</strong> {{ authStore.currentAdmin?.email }}
            </div>
            <div class="detail-item">
              <strong>Estado:</strong> 
              <span class="status-badge">Autenticado</span>
            </div>
          </div>

          <div class="actions-section">
            <h3>Acciones Disponibles:</h3>
            <div class="action-buttons">
              <button class="action-btn primary" @click="showUsers">
                Gestionar Usuarios
              </button>
              <button class="action-btn secondary" @click="showReports">
                Ver Reportes
              </button>
              <button class="action-btn success" @click="showSettings">
                Configuraciones
              </button>
            </div>
          </div>
        </div>

        <div v-if="activeSection" class="content-section">
          <div v-if="activeSection === 'users'" class="section-content">
            <h3>Gestión de Usuarios</h3>
            <p>Aquí podrás gestionar todos los usuarios del sistema.</p>
            <div class="placeholder-content">
              <p>🔧 Funcionalidad en desarrollo...</p>
            </div>
          </div>

          <div v-if="activeSection === 'reports'" class="section-content">
            <h3>Reportes del Sistema</h3>
            <p>Visualiza estadísticas y reportes importantes.</p>
            <div class="placeholder-content">
              <p>📊 Funcionalidad en desarrollo...</p>
            </div>
          </div>

          <div v-if="activeSection === 'settings'" class="section-content">
            <h3>Configuraciones</h3>
            <p>Ajusta las configuraciones del sistema.</p>
            <div class="placeholder-content">
              <p>⚙️ Funcionalidad en desarrollo...</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeSection = ref<string | null>(null)

onMounted(() => {
  // Verificar que el usuario esté autenticado
  if (!authStore.isLoggedIn) {
    router.push('/login')
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const showUsers = () => {
  activeSection.value = activeSection.value === 'users' ? null : 'users'
}

const showReports = () => {
  activeSection.value = activeSection.value === 'reports' ? null : 'reports'
}

const showSettings = () => {
  activeSection.value = activeSection.value === 'settings' ? null : 'settings'
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dashboard-header {
  background-color: #343a40;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  margin: 0;
  font-size: 1.5rem;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #c82333;
}

.dashboard-main {
  padding: 2rem 0;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.welcome-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.welcome-card h2 {
  margin-top: 0;
  color: #333;
}

.admin-details {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 6px;
  margin: 1.5rem 0;
}

.admin-details h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #495057;
}

.detail-item {
  margin-bottom: 0.5rem;
}

.status-badge {
  background-color: #28a745;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.actions-section {
  margin-top: 2rem;
}

.actions-section h3 {
  margin-bottom: 1rem;
  color: #495057;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.action-btn.primary {
  background-color: #007bff;
  color: white;
}

.action-btn.primary:hover {
  background-color: #0056b3;
}

.action-btn.secondary {
  background-color: #6c757d;
  color: white;
}

.action-btn.secondary:hover {
  background-color: #545b62;
}

.action-btn.success {
  background-color: #28a745;
  color: white;
}

.action-btn.success:hover {
  background-color: #218838;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-content h3 {
  margin-top: 0;
  color: #333;
}

.placeholder-content {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 6px;
  text-align: center;
  margin-top: 1rem;
  border: 2px dashed #dee2e6;
}

.placeholder-content p {
  margin: 0;
  font-size: 1.1rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .admin-info {
    flex-direction: column;
    gap: 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>