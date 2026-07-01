import apiClient from './client'
import { User, AuthToken } from '../types'

export interface RegisterData {
  email: string
  username: string
  password: string
  first_name?: string
  last_name?: string
  phone?: string
}

export interface LoginData {
  email: string
  password: string
}

export async function register(data: RegisterData): Promise<User> {
  const response = await apiClient.post<User>('/auth/register', data)
  return response.data
}

export async function login(data: LoginData): Promise<AuthToken> {
  const response = await apiClient.post<AuthToken>('/auth/login', data)
  return response.data
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>('/auth/me')
  return response.data
}

export async function updateUser(data: Partial<User>): Promise<User> {
  const response = await apiClient.put<User>('/auth/me', data)
  return response.data
}

export function logout(): void {
  localStorage.removeItem('authToken')
  localStorage.removeItem('user')
}
