import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AppState, NotificationData } from '@/types'

interface AppStore extends AppState {
  // Theme actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleTheme: () => void

  // Sidebar actions
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void

  // Notification actions
  addNotification: (notification: Omit<NotificationData, 'id'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  // General UI actions
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      theme: 'system',
      sidebarOpen: true,
      notifications: [],

      // Theme actions
      setTheme: (theme) => {
        set({ theme })

        // Apply theme to document
        const root = document.documentElement
        root.classList.remove('light', 'dark')

        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
          root.classList.add(systemTheme)
        } else {
          root.classList.add(theme)
        }
      },

      toggleTheme: () => {
        const { theme } = get()
        const newTheme = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light'
        get().setTheme(newTheme)
      },

      // Sidebar actions
      setSidebarOpen: (open) => {
        set({ sidebarOpen: open })
      },

      toggleSidebar: () => {
        const { sidebarOpen } = get()
        set({ sidebarOpen: !sidebarOpen })
      },

      // Notification actions
      addNotification: (notification) => {
        const id = Math.random().toString(36).substr(2, 9)
        const newNotification = { ...notification, id }

        set(state => ({
          notifications: [...state.notifications, newNotification]
        }))

        // Auto-remove notification after duration
        if (!notification.persistent) {
          const duration = notification.duration || 5000
          setTimeout(() => {
            get().removeNotification(id)
          }, duration)
        }
      },

      removeNotification: (id) => {
        set(state => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }))
      },

      clearNotifications: () => {
        set({ notifications: [] })
      },

      // General UI actions
      setLoading: (loading) => {
        // This could be used for global loading states
        console.log('Global loading state:', loading)
      },
    }),
    {
      name: 'sentrix-app',
      partialize: (state) => ({
        theme: state.theme,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
)

// Initialize theme on store creation
const initializeTheme = () => {
  const { theme, setTheme } = useAppStore.getState()
  setTheme(theme)
}

// Listen for system theme changes
if (typeof window !== 'undefined') {
  initializeTheme()

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const { theme, setTheme } = useAppStore.getState()
    if (theme === 'system') {
      setTheme('system') // Re-apply system theme
    }
  })
}

// Computed selectors
export const useTheme = () => useAppStore(state => state.theme)
export const useSidebarOpen = () => useAppStore(state => state.sidebarOpen)
export const useNotifications = () => useAppStore(state => state.notifications)