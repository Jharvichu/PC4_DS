import apiClient from './client'
import { Pet, PetCreateInput } from '../types'

export async function createPet(data: PetCreateInput): Promise<Pet> {
  const response = await apiClient.post<Pet>('/pets/', data)
  return response.data
}

export async function getMyPets(): Promise<Pet[]> {
  const response = await apiClient.get<Pet[]>('/pets/me')
  return response.data
}

export async function getPet(petId: string): Promise<Pet> {
  const response = await apiClient.get<Pet>(`/pets/${petId}`)
  return response.data
}

export async function deletePet(petId: string): Promise<void> {
  await apiClient.delete(`/pets/${petId}`)
}
