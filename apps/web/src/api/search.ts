import apiClient from './client'
import { ImageSearchRequestInput, ImageSearchResult } from '../types'

export async function searchByImage(data: ImageSearchRequestInput): Promise<ImageSearchResult> {
  const response = await apiClient.post<ImageSearchResult>('/search/', data)
  return response.data
}

export async function getSearch(searchId: string): Promise<ImageSearchResult> {
  const response = await apiClient.get<ImageSearchResult>(`/search/${searchId}`)
  return response.data
}
