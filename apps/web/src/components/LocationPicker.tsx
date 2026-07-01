import { useEffect, useState } from 'react'
import { useGeolocation } from '../hooks/useGeolocation'
import MapPicker from './MapPicker'
import { GeoPoint } from '../types'

interface LocationPickerProps {
  value: GeoPoint | null
  onChange: (point: GeoPoint) => void
}

export default function LocationPicker({ value, onChange }: LocationPickerProps) {
  const { coords, isLoading, error, requestLocation } = useGeolocation()
  const [manualLat, setManualLat] = useState('')
  const [manualLon, setManualLon] = useState('')

  useEffect(() => {
    if (coords) {
      onChange(coords)
      setManualLat(String(coords.latitude))
      setManualLon(String(coords.longitude))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [coords])

  const applyManual = () => {
    const lat = parseFloat(manualLat)
    const lon = parseFloat(manualLon)
    if (!Number.isNaN(lat) && !Number.isNaN(lon)) {
      onChange({ latitude: lat, longitude: lon })
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={requestLocation}
          className="btn btn-secondary"
          disabled={isLoading}
        >
          {isLoading ? 'Obteniendo ubicación...' : '📍 Usar mi ubicación GPS'}
        </button>
        {value && (
          <span className="text-sm text-gray-600">
            {value.latitude.toFixed(5)}, {value.longitude.toFixed(5)}
          </span>
        )}
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <MapPicker value={value} onChange={onChange} />
      <p className="text-xs text-gray-500">Haz clic en el mapa o arrastra el marcador para ajustar la ubicación.</p>

      <details className="text-sm">
        <summary className="cursor-pointer text-gray-600">Ingresar coordenadas manualmente ▾</summary>
        <div className="grid grid-cols-2 gap-3 mt-2">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">Latitud (manual)</label>
            <input
              type="number"
              step="any"
              className="input"
              value={manualLat}
              onChange={(e) => setManualLat(e.target.value)}
              onBlur={applyManual}
            />
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">Longitud (manual)</label>
            <input
              type="number"
              step="any"
              className="input"
              value={manualLon}
              onChange={(e) => setManualLon(e.target.value)}
              onBlur={applyManual}
            />
          </div>
        </div>
      </details>
    </div>
  )
}
