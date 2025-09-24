// Tipos para Vue Router con meta fields personalizados
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    requiresGuest?: boolean
    title?: string
  }
}

export {}