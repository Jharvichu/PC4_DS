import apiClient from './client'
import { Notification, NotificationPreference, NotificationPreferenceInput } from '../types'

export async function getMyNotifications(): Promise<Notification[]> {
  const response = await apiClient.get<Notification[]>('/notifications/')
  return response.data
}

export async function markAsRead(notificationId: string): Promise<Notification> {
  const response = await apiClient.put<Notification>(`/notifications/${notificationId}/read`)
  return response.data
}

export async function getMyPreferences(): Promise<NotificationPreference> {
  const response = await apiClient.get<NotificationPreference>('/notifications/preferences/me')
  return response.data
}

export async function updateMyPreferences(data: NotificationPreferenceInput): Promise<NotificationPreference> {
  const response = await apiClient.put<NotificationPreference>('/notifications/preferences/me', data)
  return response.data
}
