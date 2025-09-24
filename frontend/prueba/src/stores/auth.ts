import { defineStore } from 'pinia'
import axios from 'axios'

// Configurar la URL base del backend Django
const API_URL = 'http://127.0.0.1:8000/api'

export interface Admin {
  id: number
  email: string
  name: string
  is_staff: boolean
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface CreateAdminCredentials {
  first_name: string
  last_name: string
  email: string
  password: string
  password_confirm: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    admin: null as Admin | null,
    tokens: null as AuthTokens | null,
    isAuthenticated: false,
    loading: false,
    error: null as string | null,
    tokenExpiry: null as Date | null
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.admin,
    currentAdmin: (state) => state.admin
  },

  actions: {
    // Inicializar la autenticación desde localStorage
    initAuth() {
      const tokens = localStorage.getItem('admin_tokens')
      const adminData = localStorage.getItem('admin_data')
      const tokenExpiry = localStorage.getItem('token_expiry')
      
      if (tokens && adminData && tokenExpiry) {
        try {
          this.tokens = JSON.parse(tokens)
          this.admin = JSON.parse(adminData)
          this.tokenExpiry = new Date(tokenExpiry)
          
          // Verificar si el token no ha expirado
          if (this.tokenExpiry && this.tokenExpiry > new Date()) {
            this.isAuthenticated = true
            // Configurar el header de autorización para axios
            axios.defaults.headers.common['Authorization'] = `Bearer ${this.tokens?.access_token}`
          } else {
            // Token expirado, limpiar
            this.logout()
          }
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
        const response = await axios.post(`${API_URL}/admin/login/`, {
          email: credentials.email,
          password: credentials.password
        })

        const { user, tokens } = response.data

        // Calcular fecha de expiración (20 minutos)
        const expiryDate = new Date()
        expiryDate.setSeconds(expiryDate.getSeconds() + tokens.expires_in)

        // Guardar en el estado
        this.admin = user
        this.tokens = tokens
        this.tokenExpiry = expiryDate
        this.isAuthenticated = true

        // Guardar en localStorage
        localStorage.setItem('admin_tokens', JSON.stringify(tokens))
        localStorage.setItem('admin_data', JSON.stringify(user))
        localStorage.setItem('token_expiry', expiryDate.toISOString())

        // Configurar header de autorización
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`

        return { success: true }
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: { message?: string } } }
        this.error = axiosError.response?.data?.message || 'Error al iniciar sesión'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // Crear administrador
    async createAdmin(credentials: CreateAdminCredentials) {
      this.loading = true
      this.error = null

      if (credentials.password !== credentials.password_confirm) {
        this.error = 'Las contraseñas no coinciden'
        this.loading = false
        return { success: false, error: this.error }
      }

      try {
        const response = await axios.post(`${API_URL}/admin/create/`, {
          first_name: credentials.first_name,
          last_name: credentials.last_name,
          email: credentials.email,
          password: credentials.password,
          password_confirm: credentials.password_confirm
        })

        const { admin } = response.data

        return { success: true, admin }
      } catch (error: unknown) {
        const axiosError = error as { response?: { data?: { message?: string; field_errors?: Record<string, string[]> } } }
        this.error = axiosError.response?.data?.message || 'Error al crear administrador'
        return { 
          success: false, 
          error: this.error,
          fieldErrors: axiosError.response?.data?.field_errors
        }
      } finally {
        this.loading = false
      }
    },

    // Cerrar sesión
    async logout() {
      // Intentar invalidar el token en el backend
      if (this.tokens?.access_token) {
        try {
          await axios.post(`${API_URL}/admin/logout/`, {}, {
            headers: {
              'Authorization': `Bearer ${this.tokens.access_token}`
            }
          })
        } catch (error) {
          // Si falla, continuamos con el logout local
          console.warn('Error al invalidar token en servidor:', error)
        }
      }

      // Limpiar estado local
      this.admin = null
      this.tokens = null
      this.tokenExpiry = null
      this.isAuthenticated = false
      this.error = null

      // Limpiar localStorage
      localStorage.removeItem('admin_tokens')
      localStorage.removeItem('admin_data')
      localStorage.removeItem('token_expiry')

      // Limpiar header de autorización
      delete axios.defaults.headers.common['Authorization']
    },

    // Verificar si el token está próximo a expirar
    isTokenExpiring(minutesBefore: number = 2) {
      if (!this.tokenExpiry) return false
      
      const now = new Date()
      const expiryThreshold = new Date(this.tokenExpiry)
      expiryThreshold.setMinutes(expiryThreshold.getMinutes() - minutesBefore)
      
      return now >= expiryThreshold
    },

    // Verificar validez del token con el servidor
    async verifyToken() {
      if (!this.tokens?.access_token) {
        return false
      }

      try {
        const response = await axios.get(`${API_URL}/admin/verify-token/`, {
          headers: {
            'Authorization': `Bearer ${this.tokens.access_token}`
          }
        })
        
        return response.data.valid
      } catch {
        // Token inválido o expirado
        this.logout()
        return false
      }
    },

    // Limpiar errores
    clearError() {
      this.error = null
    },

    // Inicializar estado desde localStorage
    initializeFromStorage() {
      try {
        const tokensData = localStorage.getItem('admin_tokens')
        const adminData = localStorage.getItem('admin_data') 
        const expiryData = localStorage.getItem('token_expiry')

        if (tokensData && adminData && expiryData) {
          this.tokens = JSON.parse(tokensData)
          this.admin = JSON.parse(adminData)
          this.tokenExpiry = new Date(expiryData)
          
          // Verificar si el token no ha expirado
          if (this.tokenExpiry > new Date()) {
            this.isAuthenticated = true
            
            // Configurar header de autorización
            if (this.tokens?.access_token) {
              axios.defaults.headers.common['Authorization'] = `Bearer ${this.tokens.access_token}`
            }
          } else {
            // Token expirado, limpiar
            this.logout()
          }
        }
      } catch (error) {
        console.warn('Error al cargar datos de autenticación:', error)
        this.logout()
      }
    }
  }
})