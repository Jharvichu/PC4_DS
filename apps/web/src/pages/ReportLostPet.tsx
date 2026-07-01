import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as petsApi from '../api/pets'
import * as reportsApi from '../api/reports'
import ImageUpload from '../components/ImageUpload'
import LocationPicker from '../components/LocationPicker'
import { GeoPoint, Pet, PetSpecies } from '../types'

export default function ReportLostPet() {
  const navigate = useNavigate()

  const [pets, setPets] = useState<Pet[]>([])
  const [selectedPetId, setSelectedPetId] = useState<string>('')
  const [showNewPetForm, setShowNewPetForm] = useState(false)

  const [petName, setPetName] = useState('')
  const [petSpecies, setPetSpecies] = useState<PetSpecies>('PERRO')
  const [petBreed, setPetBreed] = useState('')
  const [petPhoto, setPetPhoto] = useState('')

  const [location, setLocation] = useState<GeoPoint | null>(null)
  const [address, setAddress] = useState('')
  const [description, setDescription] = useState('')
  const [radiusKm, setRadiusKm] = useState(5)
  const [anonymous, setAnonymous] = useState(true)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    petsApi
      .getMyPets()
      .then((data) => {
        setPets(data)
        if (data.length === 0) setShowNewPetForm(true)
        else setSelectedPetId(data[0].id)
      })
      .catch(() => setShowNewPetForm(true))
  }, [])

  const handleCreatePet = async () => {
    if (!petName.trim()) {
      setError('El nombre de la mascota es obligatorio')
      return
    }
    if (!petPhoto) {
      setError('La foto de la mascota es obligatoria')
      return
    }
    setError('')
    setIsLoading(true)
    try {
      const pet = await petsApi.createPet({
        name: petName,
        species: petSpecies,
        breed: petBreed || undefined,
        photo_url: petPhoto,
      })
      setPets([...pets, pet])
      setSelectedPetId(pet.id)
      setShowNewPetForm(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrar la mascota')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!selectedPetId) {
      setError('Selecciona o registra una mascota')
      return
    }
    if (!location) {
      setError('Debes indicar la ubicación donde se perdió')
      return
    }
    if (description.trim().length < 10) {
      setError('La descripción debe tener al menos 10 caracteres')
      return
    }

    setIsLoading(true)
    try {
      await reportsApi.createReport({
        pet_id: selectedPetId,
        last_seen_latitude: location.latitude,
        last_seen_longitude: location.longitude,
        last_seen_address: address || undefined,
        description,
        alert_radius_km: radiusKm,
        contact_is_anonymous: anonymous,
      })
      setSuccess(true)
      setTimeout(() => navigate('/'), 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al reportar la mascota')
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
          <h1 className="text-2xl font-bold mt-2">Reportar Mascota Perdida</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl bg-white rounded-lg shadow p-8 space-y-6">
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              ¡Reporte creado! Se están enviando alertas a personas cercanas.
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>
          )}

          {showNewPetForm ? (
            <div className="space-y-4 border-b pb-6">
              <h2 className="text-xl font-bold">1. Registra tu mascota</h2>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Nombre</label>
                <input className="input" value={petName} onChange={(e) => setPetName(e.target.value)} />
              </div>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Especie</label>
                <select
                  className="input"
                  value={petSpecies}
                  onChange={(e) => setPetSpecies(e.target.value as PetSpecies)}
                >
                  <option value="PERRO">Perro</option>
                  <option value="GATO">Gato</option>
                  <option value="OTRO">Otro</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Raza (opcional)</label>
                <input className="input" value={petBreed} onChange={(e) => setPetBreed(e.target.value)} />
              </div>

              <ImageUpload label="Foto de la mascota" onChange={setPetPhoto} />

              <button type="button" className="btn btn-primary" onClick={handleCreatePet} disabled={isLoading}>
                {isLoading ? 'Guardando...' : 'Registrar Mascota'}
              </button>

              {pets.length > 0 && (
                <button
                  type="button"
                  className="btn btn-secondary ml-2"
                  onClick={() => setShowNewPetForm(false)}
                >
                  Cancelar
                </button>
              )}
            </div>
          ) : (
            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Mascota</label>
              <div className="flex gap-2">
                <select className="input" value={selectedPetId} onChange={(e) => setSelectedPetId(e.target.value)}>
                  {pets.map((pet) => (
                    <option key={pet.id} value={pet.id}>
                      {pet.name} ({pet.species})
                    </option>
                  ))}
                </select>
                <button type="button" className="btn btn-secondary" onClick={() => setShowNewPetForm(true)}>
                  + Nueva
                </button>
              </div>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmitReport}>
            <h2 className="text-xl font-bold">2. Detalles de la pérdida</h2>

            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Ubicación donde se perdió</label>
              <LocationPicker value={location} onChange={setLocation} />
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Dirección de referencia (opcional)</label>
              <input className="input" value={address} onChange={(e) => setAddress(e.target.value)} />
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">Descripción</label>
              <textarea
                className="input"
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Color, tamaño, collar, comportamiento, última vez visto..."
              />
            </div>

            <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Radio de alerta: {radiusKm} km
              </label>
              <input
                type="range"
                min={1}
                max={20}
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="anonymous"
                checked={anonymous}
                onChange={(e) => setAnonymous(e.target.checked)}
              />
              <label htmlFor="anonymous" className="text-gray-700">
                Mantener mis datos de contacto anónimos ante quienes reporten avistamientos
              </label>
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={isLoading}>
              {isLoading ? 'Enviando...' : 'Reportar Mascota Perdida'}
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
