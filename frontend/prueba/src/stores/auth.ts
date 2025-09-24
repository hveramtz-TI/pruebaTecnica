import { defineStore } from 'pinia'
import axios from 'axios'

// Configurar la URL base del backend Django
const API_URL = 'http://localhost:8000/api'

export interface Admin {
  id: number
  email: string
  token?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  password: string
  confirmPassword: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    admin: null as Admin | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.admin,
    currentAdmin: (state) => state.admin
  },

  actions: {
    // Inicializar la autenticación desde localStorage
    initAuth() {
      const token = localStorage.getItem('admin_token')
      const adminData = localStorage.getItem('admin_data')
      
      if (token && adminData) {
        try {
          this.admin = JSON.parse(adminData)
          this.isAuthenticated = true
          // Configurar el header de autorización para axios
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        } catch {
          this.logout()
        }
      }
    },

    // Iniciar sesión
    async login(credentials: LoginCredentials) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`${API_URL}/auth/login/`, {
          email: credentials.email,
          password: credentials.password
        })

        const { admin, token } = response.data

        // Guardar en el estado
        this.admin = admin
        this.isAuthenticated = true

        // Guardar en localStorage
        localStorage.setItem('admin_token', token)
        localStorage.setItem('admin_data', JSON.stringify(admin))

        // Configurar header de autorización
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

        return { success: true }
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: { message?: string } } }
        this.error = axiosError.response?.data?.message || 'Error al iniciar sesión'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // Registrarse
    async register(credentials: RegisterCredentials) {
      this.loading = true
      this.error = null

      if (credentials.password !== credentials.confirmPassword) {
        this.error = 'Las contraseñas no coinciden'
        this.loading = false
        return { success: false, error: this.error }
      }

      try {
        const response = await axios.post(`${API_URL}/auth/register/`, {
          email: credentials.email,
          password: credentials.password
        })

        const { admin, token } = response.data

        // Guardar en el estado
        this.admin = admin
        this.isAuthenticated = true

        // Guardar en localStorage
        localStorage.setItem('admin_token', token)
        localStorage.setItem('admin_data', JSON.stringify(admin))

        // Configurar header de autorización
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

        return { success: true }
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: { message?: string } } }
        this.error = axiosError.response?.data?.message || 'Error al registrarse'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // Cerrar sesión
    logout() {
      this.admin = null
      this.isAuthenticated = false
      this.error = null

      // Limpiar localStorage
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_data')

      // Limpiar header de autorización
      delete axios.defaults.headers.common['Authorization']
    },

    // Limpiar errores
    clearError() {
      this.error = null
    }
  }
})