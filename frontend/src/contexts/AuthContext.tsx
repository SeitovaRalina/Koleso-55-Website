import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'
import type { User, AuthTokens } from '../types'
import {
  getAuthToken,
  setAuthToken,
  setRefreshToken,
  clearAuthTokens,
} from '../utils/session'
import { authApi } from '../api/auth'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (tokens: AuthTokens, user: User) => void
  logout: () => Promise<void>
  updateUser: (user: User) => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      const token = getAuthToken()
      if (token) {
        try {
          const userData = await authApi.getProfile()
          setUser(userData)
          setIsAuthenticated(true)
        } catch (error) {
          console.error('Failed to fetch user profile:', error)
          clearAuthTokens()
          setIsAuthenticated(false)
        }
      }
      setIsLoading(false)
    }

    loadUser()
  }, [])

  const login = (tokens: AuthTokens, userData: User) => {
    setAuthToken(tokens.access)
    setRefreshToken(tokens.refresh)
    setUser(userData)
    setIsAuthenticated(true)
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearAuthTokens()
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const updateUser = (userData: User) => {
    setUser(userData)
  }

  const refreshUser = async () => {
    try {
      const userData = await authApi.getProfile()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user profile:', error)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        updateUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
