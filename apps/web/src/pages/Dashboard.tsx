import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import * as reportsApi from '../api/reports'
import { Report } from '../types'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [myReports, setMyReports] = useState<Report[]>([])

  useEffect(() => {
    reportsApi.getMyReports().then(setMyReports).catch(() => {})
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleMarkFound = async (reportId: string) => {
    try {
      const updated = await reportsApi.updateReportStatus(reportId, 'ENCONTRADO')
      setMyReports((prev) => prev.map((r) => (r.id === reportId ? updated : r)))
    } catch {
      // no-op
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Sistema de Mascotas Perdidas</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">{user?.username}</span>
            <button onClick={handleLogout} className="btn btn-secondary">
              Cerrar sesión
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Report Lost Pet Card */}
          <div
            className="card p-6 cursor-pointer hover:shadow-lg transition-all"
            onClick={() => navigate('/report-lost-pet')}
          >
            <div className="text-4xl mb-4">🐾</div>
            <h2 className="text-xl font-bold mb-2">Reportar Mascota Perdida</h2>
            <p className="text-gray-600">
              Registra tu mascota perdida y recibirás alertas de ciudadanos que la hayan visto.
            </p>
          </div>

          {/* Sighting Card */}
          <div
            className="card p-6 cursor-pointer hover:shadow-lg transition-all"
            onClick={() => navigate('/sighting')}
          >
            <div className="text-4xl mb-4">👀</div>
            <h2 className="text-xl font-bold mb-2">Reportar Avistamiento</h2>
            <p className="text-gray-600">
              ¿Viste una mascota perdida? Reporta su ubicación y foto para ayudar a encontrarla.
            </p>
          </div>

          {/* Image Search Card */}
          <div
            className="card p-6 cursor-pointer hover:shadow-lg transition-all"
            onClick={() => navigate('/search')}
          >
            <div className="text-4xl mb-4">🔍</div>
            <h2 className="text-xl font-bold mb-2">Buscar por Imagen</h2>
            <p className="text-gray-600">
              Sube una foto para buscar mascotas perdidas, en adopción o venta.
            </p>
          </div>

          {/* Caregiver Network Card */}
          <div
            className="card p-6 cursor-pointer hover:shadow-lg transition-all"
            onClick={() => navigate('/caregivers')}
          >
            <div className="text-4xl mb-4">💜</div>
            <h2 className="text-xl font-bold mb-2">Red de Cuidadores</h2>
            <p className="text-gray-600">
              Conecta con cuidadores de mascotas y comparte responsabilidades.
            </p>
          </div>

          {/* Notifications Card */}
          <div
            className="card p-6 cursor-pointer hover:shadow-lg transition-all"
            onClick={() => navigate('/notifications')}
          >
            <div className="text-4xl mb-4">🔔</div>
            <h2 className="text-xl font-bold mb-2">Notificaciones</h2>
            <p className="text-gray-600">
              Revisa las alertas y ajusta tu radio y canales de notificación.
            </p>
          </div>
        </div>

        {/* My Active Reports */}
        {myReports.length > 0 && (
          <section className="mt-10">
            <h2 className="text-xl font-bold mb-4">Mis Reportes</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {myReports.map((report) => (
                <div key={report.id} className="card p-4">
                  <div className="flex justify-between items-start">
                    <span className="font-bold">Reporte #{report.id.slice(0, 8)}</span>
                    <span
                      className={`text-xs font-bold px-2 py-1 rounded ${
                        report.status === 'ACTIVO'
                          ? 'bg-yellow-100 text-yellow-700'
                          : report.status === 'ENCONTRADO'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {report.status}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{report.description}</p>
                  {report.status === 'ACTIVO' && (
                    <button className="btn btn-secondary mt-3" onClick={() => handleMarkFound(report.id)}>
                      Marcar como Encontrado
                    </button>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Info Section */}
        <section className="mt-12 bg-blue-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">¿Cómo funciona?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-bold text-lg mb-2">1. Reporta</h3>
              <p className="text-gray-700">
                Reporta tu mascota perdida con fotos, descripción y ubicación.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">2. Alertas</h3>
              <p className="text-gray-700">
                Ciudadanos cercanos reciben alertas sobre tu mascota en tiempo real.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">3. Encuentra</h3>
              <p className="text-gray-700">
                Recibe avistamientos y conecta directamente con quien vio a tu mascota.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
