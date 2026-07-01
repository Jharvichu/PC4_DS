import apiClient from './client'
import { Sighting, SightingCreateInput } from '../types'

export async function createSighting(data: SightingCreateInput): Promise<Sighting> {
  const response = await apiClient.post<Sighting>('/sightings/', data)
  return response.data
}

export async function getSightingsForReport(reportId: string): Promise<Sighting[]> {
  const response = await apiClient.get<Sighting[]>(`/sightings/report/${reportId}`)
  return response.data
}
