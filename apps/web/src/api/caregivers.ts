import apiClient from './client'
import { Caregiver, CaregiverRegisterInput, CaregiverRating, CaregiverRatingInput } from '../types'

export async function registerCaregiver(data: CaregiverRegisterInput): Promise<Caregiver> {
  const response = await apiClient.post<Caregiver>('/caregivers/', data)
  return response.data
}

export async function listCaregivers(roleType?: string, species?: string): Promise<Caregiver[]> {
  const params: Record<string, string> = {}
  if (roleType) params.role_type = roleType
  if (species) params.species = species
  const response = await apiClient.get<Caregiver[]>('/caregivers/', { params })
  return response.data
}

export async function getMyCaregiverProfile(): Promise<Caregiver> {
  const response = await apiClient.get<Caregiver>('/caregivers/me')
  return response.data
}

export async function getCaregiver(caregiverId: string): Promise<Caregiver> {
  const response = await apiClient.get<Caregiver>(`/caregivers/${caregiverId}`)
  return response.data
}

export async function updateRestrictions(data: {
  accepted_species?: string[]
  accepted_sizes?: string[]
  can_administer_medication?: boolean
}): Promise<Caregiver> {
  const response = await apiClient.put<Caregiver>('/caregivers/me/restrictions', data)
  return response.data
}

export async function toggleAlerts(receivesAlerts: boolean): Promise<Caregiver> {
  const response = await apiClient.put<Caregiver>('/caregivers/me/alerts-toggle', {
    receives_alerts: receivesAlerts,
  })
  return response.data
}

export async function submitIdentityDocument(documentUrl: string): Promise<Caregiver> {
  const response = await apiClient.post<Caregiver>('/caregivers/me/identity-document', {
    document_url: documentUrl,
  })
  return response.data
}

export async function addRating(caregiverId: string, data: CaregiverRatingInput): Promise<CaregiverRating> {
  const response = await apiClient.post<CaregiverRating>(`/caregivers/${caregiverId}/ratings`, data)
  return response.data
}

export async function getRatings(caregiverId: string): Promise<CaregiverRating[]> {
  const response = await apiClient.get<CaregiverRating[]>(`/caregivers/${caregiverId}/ratings`)
  return response.data
}
