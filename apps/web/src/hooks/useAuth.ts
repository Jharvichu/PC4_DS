import { useEffect, useState } from 'react'
import { User } from '../types'
import * as authApi from '../api/auth'

interface UseAuthReturn {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: authApi.RegisterData) => Promise<void>
  logout: () => void
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('authToken')
        if (token) {
          const currentUser = await authApi.getCurrentUser()
          setUser(currentUser)
          localStorage.setItem('user', JSON.stringify(currentUser))
        }
      } catch (error) {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password })
      localStorage.setItem('authToken', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      setUser(response.user)
    } catch (error) {
      throw error
    }
  }

  const register = async (data: authApi.RegisterData) => {
    try {
      await authApi.register(data)
      // Auto-login after registration
      await login(data.email, data.password)
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    authApi.logout()
    setUser(null)
  }

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }
}
