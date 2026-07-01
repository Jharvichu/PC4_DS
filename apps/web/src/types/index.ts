// User types
export interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  phone?: string
  role: string
  location?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  user: User
}

// Pet types
export type PetSpecies = 'PERRO' | 'GATO' | 'OTRO'

export interface Pet {
  id: string
  owner_id: string
  name: string
  species: string
  breed?: string
  photo_url?: string
  description?: string
  microchip_id?: string
  created_at: string
}

export interface PetCreateInput {
  name: string
  species: PetSpecies
  breed?: string
  photo_url: string
  description?: string
  microchip_id?: string
}

// Report types (RF 1.1, 1.2, 1.4)
export type ReportStatus = 'ACTIVO' | 'ENCONTRADO' | 'CANCELADO'

export interface ReportPublic {
  id: string
  pet_id: string
  status: string
  last_seen_latitude: number
  last_seen_longitude: number
  last_seen_address?: string
  last_seen_date: string
  description?: string
  created_at: string
}

export interface Report extends ReportPublic {
  owner_id: string
  alert_radius_km: number
  contact_is_anonymous: boolean
  found_date?: string
}

export interface ReportCreateInput {
  pet_id: string
  last_seen_latitude: number
  last_seen_longitude: number
  last_seen_address?: string
  description: string
  alert_radius_km: number
  contact_is_anonymous: boolean
}

// Sighting types (RF 1.3)
export type ConfidenceLevel = 'ALTA' | 'MEDIA' | 'BAJA'

export interface Sighting {
  id: string
  report_id: string
  latitude: number
  longitude: number
  photo_url: string
  description?: string
  confidence_level: string
  created_at: string
}

export interface SightingCreateInput {
  report_id: string
  latitude: number
  longitude: number
  photo_url: string
  description?: string
  confidence_level: ConfidenceLevel
}

// Search types (RF 2.1-2.5)
export type SearchIntentValue = 'ADOPCION' | 'VENTA' | 'VERIFICAR_PERDIDA'

export const SEARCH_INTENTS: { value: SearchIntentValue; label: string }[] = [
  { value: 'ADOPCION', label: 'Adopción' },
  { value: 'VENTA', label: 'Venta' },
  { value: 'VERIFICAR_PERDIDA', label: 'Verificar Pérdida' },
]

export interface SearchResultItem {
  id: string
  title: string
  description?: string
  image_url?: string
  relevance_score: number
  source: string
  url?: string
}

export interface ImageSearchRequestInput {
  image_url: string
  intent: SearchIntentValue
  metadata?: Record<string, unknown>
}

export interface ImageSearchResult {
  id: string
  intent: string
  status: string
  results: SearchResultItem[]
  created_at: string
}

// Caregiver types (RF 3.1-3.4)
export type CaregiverRoleType = 'SOLIDARIO' | 'PROFESIONAL' | 'ESPECIALIZADO'
export type VerificationStatus = 'PENDIENTE' | 'APROBADO' | 'RECHAZADO'

export interface Caregiver {
  id: string
  user_id: string
  role_type: string
  accepted_species?: string
  accepted_sizes?: string
  can_administer_medication: boolean
  specialization?: string
  id_verification_status: string
  is_public: boolean
  receives_alerts: boolean
  rating_average: number
  rating_count: number
  created_at: string
}

export interface CaregiverRegisterInput {
  role_type: CaregiverRoleType
  accepted_species?: string[]
  accepted_sizes?: string[]
  can_administer_medication: boolean
  specialization?: string
}

export interface CaregiverRating {
  id: string
  caregiver_id: string
  score: number
  comment?: string
  created_at: string
}

export interface CaregiverRatingInput {
  score: number
  comment?: string
  report_id: string
}

// Notification types
export interface Notification {
  id: string
  user_id: string
  report_id?: string
  sighting_id?: string
  type: string
  content: string
  is_read: boolean
  channel: string
  created_at: string
}

export interface NotificationPreference {
  id: string
  user_id: string
  latitude?: number
  longitude?: number
  radius_km: number
  push_enabled: boolean
  sms_enabled: boolean
  email_enabled: boolean
  alerts_active: boolean
}

export interface NotificationPreferenceInput {
  latitude?: number
  longitude?: number
  radius_km?: number
  push_enabled?: boolean
  sms_enabled?: boolean
  email_enabled?: boolean
  alerts_active?: boolean
}

// Location types
export interface GeoPoint {
  latitude: number
  longitude: number
  address?: string
}
