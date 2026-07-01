import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as caregiversApi from '../api/caregivers'
import RateCaregiver from '../components/RateCaregiver'
import { Caregiver, CaregiverRoleType } from '../types'

type Tab = 'browse' | 'profile'

export default function CaregiverNetwork() {
  const navigate = useNavigate()
  const [tab, setTab] = useState<Tab>('browse')

  const [caregivers, setCaregivers] = useState<Caregiver[]>([])
  const [roleFilter, setRoleFilter] = useState('')
  const [loadingList, setLoadingList] = useState(false)

  const [myProfile, setMyProfile] = useState<Caregiver | null>(null)
  const [hasProfile, setHasProfile] = useState(false)
  const [roleType, setRoleType] = useState<CaregiverRoleType>('SOLIDARIO')
  const [species, setSpecies] = useState('')
  const [medication, setMedication] = useState(false)
  const [specialization, setSpecialization] = useState('')
  const [documentUrl, setDocumentUrl] = useState('')

  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const loadList = () => {
    setLoadingList(true)
    caregiversApi
      .listCaregivers(roleFilter || undefined)
      .then(setCaregivers)
      .catch(() => setError('No se pudo cargar la lista de cuidadores'))
      .finally(() => setLoadingList(false))
  }

  const loadMyProfile = () => {
    caregiversApi
      .getMyCaregiverProfile()
      .then((profile) => {
        setMyProfile(profile)
        setHasProfile(true)
      })
      .catch(() => setHasProfile(false))
  }

  useEffect(() => {
    loadList()
    loadMyProfile()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (tab === 'browse') loadList()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [roleFilter, tab])

  const handleRegister = async () => {
    setError('')
    setMessage('')
    try {
      const profile = await caregiversApi.registerCaregiver({
        role_type: roleType,
        accepted_species: species ? species.split(',').map((s) => s.trim()) : undefined,
        can_administer_medication: medication,
        specialization: roleType === 'ESPECIALIZADO' ? specialization : undefined,
      })
      setMyProfile(profile)
      setHasProfile(true)
      setMessage('¡Perfil de cuidador creado!')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrarse como cuidador')
    }
  }

  const handleToggleAlerts = async () => {
    if (!myProfile) return
    try {
      const updated = await caregiversApi.toggleAlerts(!myProfile.receives_alerts)
      setMyProfile(updated)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar preferencia de alertas')
    }
  }

  const handleSubmitDocument = async () => {
    if (!documentUrl) {
      setError('Ingresa la URL del documento de identidad')
      return
    }
    try {
      const updated = await caregiversApi.submitIdentityDocument(documentUrl)
      setMyProfile(updated)
      setMessage('Documento enviado. Tu perfil será público cuando sea aprobado.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar el documento')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4">
          <button onClick={() => navigate('/')} className="text-blue-600 hover:text-blue-700">
            ← Volver
          </button>
          <h1 className="text-2xl font-bold mt-2">Red de Cuidadores</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex gap-2 mb-6">
          <button
            className={`btn ${tab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setTab('browse')}
          >
            Buscar Cuidadores
          </button>
          <button
            className={`btn ${tab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setTab('profile')}
          >
            Mi Perfil de Cuidador
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>
        )}
        {message && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {message}
          </div>
        )}

        {tab === 'browse' && (
          <div>
            <div className="mb-4">
              <select className="input max-w-xs" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                <option value="">Todos los roles</option>
                <option value="SOLIDARIO">Solidario</option>
                <option value="PROFESIONAL">Profesional</option>
                <option value="ESPECIALIZADO">Especializado</option>
              </select>
            </div>

            {loadingList ? (
              <p className="text-gray-500">Cargando...</p>
            ) : caregivers.length === 0 ? (
              <p className="text-gray-500">No hay cuidadores verificados disponibles todavía.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {caregivers.map((c) => (
                  <div key={c.id} className="card p-4">
                    <div className="flex justify-between items-start">
                      <h3 className="font-bold">{c.role_type}</h3>
                      <span className="text-yellow-500">
                        ★ {c.rating_average.toFixed(1)} ({c.rating_count})
                      </span>
                    </div>
                    {c.accepted_species && (
                      <p className="text-gray-600 text-sm">Especies: {c.accepted_species}</p>
                    )}
                    {c.specialization && <p className="text-gray-600 text-sm">Especialidad: {c.specialization}</p>}
                    <p className="text-gray-600 text-sm">
                      Medicación: {c.can_administer_medication ? 'Sí' : 'No'}
                    </p>
                    <RateCaregiver caregiverId={c.id} onRated={loadList} />
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'profile' && (
          <div className="max-w-xl bg-white rounded-lg shadow p-8 space-y-6">
            {!hasProfile ? (
              <div className="space-y-4">
                <h2 className="text-xl font-bold">Registrarme como Cuidador</h2>

                <div>
                  <label className="block text-gray-700 text-sm font-bold mb-2">Rol</label>
                  <select
                    className="input"
                    value={roleType}
                    onChange={(e) => setRoleType(e.target.value as CaregiverRoleType)}
                  >
                    <option value="SOLIDARIO">Solidario</option>
                    <option value="PROFESIONAL">Profesional</option>
                    <option value="ESPECIALIZADO">Especializado</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Especies aceptadas (separadas por coma)
                  </label>
                  <input
                    className="input"
                    placeholder="PERRO,GATO"
                    value={species}
                    onChange={(e) => setSpecies(e.target.value)}
                  />
                </div>

                {roleType === 'ESPECIALIZADO' && (
                  <div>
                    <label className="block text-gray-700 text-sm font-bold mb-2">Especialización</label>
                    <input
                      className="input"
                      value={specialization}
                      onChange={(e) => setSpecialization(e.target.value)}
                    />
                  </div>
                )}

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="medication"
                    checked={medication}
                    onChange={(e) => setMedication(e.target.checked)}
                  />
                  <label htmlFor="medication" className="text-gray-700">
                    Puedo administrar medicamentos
                  </label>
                </div>

                <button className="btn btn-primary w-full" onClick={handleRegister}>
                  Registrarme
                </button>
              </div>
            ) : (
              myProfile && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold">{myProfile.role_type}</h2>
                    <p className="text-gray-600">
                      Estado de verificación:{' '}
                      <span className="font-semibold">{myProfile.id_verification_status}</span>
                    </p>
                    <p className="text-gray-600">
                      Perfil público: {myProfile.is_public ? 'Sí' : 'No (pendiente de verificación)'}
                    </p>
                    <p className="text-yellow-500">
                      ★ {myProfile.rating_average.toFixed(1)} ({myProfile.rating_count} reseñas)
                    </p>
                  </div>

                  <div className="border-t pt-4">
                    <div className="flex items-center justify-between">
                      <span className="font-bold">Recibir alertas de mascotas perdidas</span>
                      <button
                        className={`btn ${myProfile.receives_alerts ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={handleToggleAlerts}
                      >
                        {myProfile.receives_alerts ? 'Activado' : 'Desactivado'}
                      </button>
                    </div>
                  </div>

                  {myProfile.id_verification_status !== 'APROBADO' && (
                    <div className="border-t pt-4 space-y-2">
                      <h3 className="font-bold">Verificación de Identidad</h3>
                      <p className="text-gray-500 text-sm">
                        Sube la URL de tu documento de identidad para habilitar tu perfil público.
                      </p>
                      <input
                        className="input"
                        placeholder="https://..."
                        value={documentUrl}
                        onChange={(e) => setDocumentUrl(e.target.value)}
                      />
                      <button className="btn btn-primary" onClick={handleSubmitDocument}>
                        Enviar Documento
                      </button>
                    </div>
                  )}
                </div>
              )
            )}
          </div>
        )}
      </main>
    </div>
  )
}
