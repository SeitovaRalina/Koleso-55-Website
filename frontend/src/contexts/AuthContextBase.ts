import { createContext } from 'react'
import type { AuthTokens, User } from '../types'

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (tokens: AuthTokens, user: User) => void
  logout: () => Promise<void>
  updateUser: (user: User) => void
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)
