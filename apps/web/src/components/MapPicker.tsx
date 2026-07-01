import { useEffect } from 'react'
import L from 'leaflet'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from 'react-leaflet'
import { GeoPoint } from '../types'

// Leaflet's default marker icons reference relative image paths that break under
// bundlers like Vite; re-point them at the bundled asset URLs explicitly.
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl })

const DEFAULT_CENTER: [number, number] = [-12.05, -77.05] // Lima, Perú
const DEFAULT_ZOOM = 13

interface MapPickerProps {
  value: GeoPoint | null
  onChange: (point: GeoPoint) => void
}

function ClickHandler({ onChange }: { onChange: (point: GeoPoint) => void }) {
  useMapEvents({
    click(e) {
      onChange({ latitude: e.latlng.lat, longitude: e.latlng.lng })
    },
  })
  return null
}

function RecenterOnExternalChange({ value }: { value: GeoPoint | null }) {
  const map = useMap()

  useEffect(() => {
    if (value) {
      map.setView([value.latitude, value.longitude], map.getZoom())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value?.latitude, value?.longitude])

  return null
}

export default function MapPicker({ value, onChange }: MapPickerProps) {
  const center: [number, number] = value ? [value.latitude, value.longitude] : DEFAULT_CENTER

  return (
    <div className="rounded-lg overflow-hidden border border-gray-300" style={{ height: 320 }}>
      <MapContainer center={center} zoom={DEFAULT_ZOOM} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickHandler onChange={onChange} />
        <RecenterOnExternalChange value={value} />
        {value && (
          <Marker
            position={[value.latitude, value.longitude]}
            draggable
            eventHandlers={{
              dragend: (e) => {
                const marker = e.target as L.Marker
                const pos = marker.getLatLng()
                onChange({ latitude: pos.lat, longitude: pos.lng })
              },
            }}
          />
        )}
      </MapContainer>
    </div>
  )
}
