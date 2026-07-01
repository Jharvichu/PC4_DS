import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as searchApi from '../api/search'
import ImageUpload from '../components/ImageUpload'
import { ImageSearchResult, SearchIntentValue, SEARCH_INTENTS } from '../types'

export default function ImageSearch() {
  const navigate = useNavigate()

  const [imageUrl, setImageUrl] = useState('')
  const [intent, setIntent] = useState<SearchIntentValue | ''>('')
  const [result, setResult] = useState<ImageSearchResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async () => {
    setError('')

    if (!imageUrl) {
      setError('Sube una imagen para buscar')
      return
    }
    if (!intent) {
      setError('Selecciona una intención: Adopción, Venta o Verificar Pérdida')
      return
    }

    setIsLoading(true)
    setResult(null)
    try {
      const response = await searchApi.searchByImage({ image_url: imageUrl, intent })
      setResult(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al realizar la búsqueda')
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
          <h1 className="text-2xl font-bold mt-2">Buscar por Imagen</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl bg-white rounded-lg shadow p-8 space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
          )}

          <ImageUpload label="Foto de la mascota" onChange={setImageUrl} />

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">¿Qué estás buscando?</label>
            <div className="grid grid-cols-3 gap-3">
              {SEARCH_INTENTS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setIntent(option.value)}
                  className={`btn ${intent === option.value ? 'btn-primary' : 'btn-secondary'}`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          <button className="btn btn-primary w-full" onClick={handleSearch} disabled={isLoading}>
            {isLoading ? 'Buscando...' : 'Buscar'}
          </button>

          {result && (
            <div className="border-t pt-6">
              <h2 className="text-lg font-bold mb-4">
                Resultados ({result.results.length}) — {result.intent}
              </h2>

              {result.results.length === 0 ? (
                <p className="text-gray-500">No se encontraron coincidencias.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {result.results.map((item) => (
                    <div key={item.id} className="card p-4">
                      {item.image_url && (
                        <img src={item.image_url} alt={item.title} className="w-full h-32 object-cover rounded mb-2" />
                      )}
                      <h3 className="font-bold">{item.title}</h3>
                      {item.description && <p className="text-gray-600 text-sm">{item.description}</p>}
                      <p className="text-gray-400 text-xs mt-1">
                        Relevancia: {(item.relevance_score * 100).toFixed(0)}% · {item.source}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
