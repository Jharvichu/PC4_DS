import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as reportsApi from '../api/reports'
import * as sightingsApi from '../api/sightings'
import ImageUpload from '../components/ImageUpload'
import LocationPicker from '../components/LocationPicker'
import { ConfidenceLevel, GeoPoint, ReportPublic } from '../types'

export default function SightingForm() {
  const navigate = useNavigate()

  const [activeReports, setActiveReports] = useState<ReportPublic[]>([])
  const [selectedReportId, setSelectedReportId] = useState('')
  const [photoUrl, setPhotoUrl] = useState('')
  const [location, setLocation] = useState<GeoPoint | null>(null)
  const [description, setDescription] = useState('')
  const [confidence, setConfidence] = useState<ConfidenceLevel>('MEDIA')

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    reportsApi
      .getActiveReports()
      .then((reports) => {
        setActiveReports(reports)
        if (reports.length > 0) setSelectedReportId(reports[0].id)
      })
      .catch(() => setError('No se pudieron cargar los reportes activos'))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!selectedReportId) {
      setError('Selecciona la mascota que viste')
      return
    }
    if (!photoUrl) {
      setError('Sube una foto del avistamiento')
      return
    }
    if (!location) {
      setError('Indica dónde la viste')
      return
    }

    setIsLoading(true)
    try {
      await sightingsApi.createSighting({
        report_id: selectedReportId,
        latitude: location.latitude,
        longitude: location.longitude,
        photo_url: photoUrl,
        description: description || undefined,
        confidence_level: confidence,
      })
      setSuccess(true)
      setTimeout(() => navigate('/'), 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al reportar el avistamiento')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4">
          <button onClick={() => navigate('/')} className="text-blue-600 hover:text-blue-700">
            ← Volver
          </button>
          <h1 className="text-2xl font-bold mt-2">Reportar Avistamiento</h1>
          <p className="text-gray-500 text-sm mt-1">
            Puedes reportar de forma anónima. El dueño no verá tu identidad.
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl bg-white rounded-lg shadow p-8 space-y-4">
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ¡Gracias! Notificamos al dueño de inmediato.
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
          )}

          {activeReports.length === 0 ? (
            <p className="text-gray-500 py-8 text-center">
              No hay reportes de mascotas perdidas activos por el momento.
            </p>
          ) : (
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">¿Cuál mascota viste?</label>
                <select
                  className="input"
                  value={selectedReportId}
                  onChange={(e) => setSelectedReportId(e.target.value)}
                >
                  {activeReports.map((report) => (
                    <option key={report.id} value={report.id}>
                      Reporte #{report.id.slice(0, 8)} — {report.description?.slice(0, 60)}
                    </option>
                  ))}
                </select>
              </div>

              <ImageUpload label="Foto del avistamiento" onChange={setPhotoUrl} />

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">¿Dónde la viste?</label>
                <LocationPicker value={location} onChange={setLocation} />
              </div>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Descripción (opcional)</label>
                <textarea
                  className="input"
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Hora aproximada, dirección de movimiento, estado del animal..."
                />
              </div>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  ¿Qué tan seguro estás de que es la misma mascota?
                </label>
                <select
                  className="input"
                  value={confidence}
                  onChange={(e) => setConfidence(e.target.value as ConfidenceLevel)}
                >
                  <option value="ALTA">Alta</option>
                  <option value="MEDIA">Media</option>
                  <option value="BAJA">Baja</option>
                </select>
              </div>

              <button type="submit" className="btn btn-primary w-full" disabled={isLoading}>
                {isLoading ? 'Enviando...' : 'Reportar Avistamiento'}
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  )
}
