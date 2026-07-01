import { useState } from 'react'
import { GeoPoint } from '../types'

interface UseGeolocationReturn {
  coords: GeoPoint | null
  isLoading: boolean
  error: string | null
  requestLocation: () => void
}

export function useGeolocation(): UseGeolocationReturn {
  const [coords, setCoords] = useState<GeoPoint | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setError('Tu navegador no soporta geolocalización')
      return
    }

    setIsLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setCoords({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        })
        setIsLoading(false)
      },
      (err) => {
        setError(err.message || 'No se pudo obtener la ubicación')
        setIsLoading(false)
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  return { coords, isLoading, error, requestLocation }
}
