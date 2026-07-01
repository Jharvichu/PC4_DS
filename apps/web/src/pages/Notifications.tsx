import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as notificationsApi from '../api/notifications'
import { Notification, NotificationPreference } from '../types'

export default function Notifications() {
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null)
  const [radiusKm, setRadiusKm] = useState(5)
  const [pushEnabled, setPushEnabled] = useState(true)
  const [smsEnabled, setSmsEnabled] = useState(false)
  const [emailEnabled, setEmailEnabled] = useState(true)
  const [alertsActive, setAlertsActive] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    notificationsApi.getMyNotifications().then(setNotifications).catch(() => {})
    notificationsApi.getMyPreferences().then((prefs) => {
      setPreferences(prefs)
      setRadiusKm(prefs.radius_km)
      setPushEnabled(prefs.push_enabled)
      setSmsEnabled(prefs.sms_enabled)
      setEmailEnabled(prefs.email_enabled)
      setAlertsActive(prefs.alerts_active)
    }).catch(() => {})
  }, [])

  const handleMarkAsRead = async (id: string) => {
    try {
      const updated = await notificationsApi.markAsRead(id)
      setNotifications((prev) => prev.map((n) => (n.id === id ? updated : n)))
    } catch {
      // no-op
    }
  }

  const handleSavePreferences = async () => {
    setError('')
    setMessage('')
    try {
      const updated = await notificationsApi.updateMyPreferences({
        radius_km: radiusKm,
        push_enabled: pushEnabled,
        sms_enabled: smsEnabled,
        email_enabled: emailEnabled,
        alerts_active: alertsActive,
      })
      setPreferences(updated)
      setMessage('Preferencias guardadas')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar preferencias')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-4">
          <button onClick={() => navigate('/')} className="text-blue-600 hover:text-blue-700">
            ← Volver
          </button>
          <h1 className="text-2xl font-bold mt-2">Notificaciones</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-lg font-bold">Mis Notificaciones</h2>
          {notifications.length === 0 ? (
            <p className="text-gray-500">No tienes notificaciones todavía.</p>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`card p-4 cursor-pointer ${n.is_read ? 'opacity-60' : ''}`}
                onClick={() => handleMarkAsRead(n.id)}
              >
                <div className="flex justify-between">
                  <span className="font-bold text-sm">{n.type}</span>
                  <span className="text-gray-400 text-xs">{n.channel}</span>
                </div>
                <p className="text-gray-700">{n.content}</p>
              </div>
            ))
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6 h-fit space-y-4">
          <h2 className="text-lg font-bold">Preferencias de Alertas</h2>

          {error && <div className="bg-red-100 text-red-700 px-3 py-2 rounded text-sm">{error}</div>}
          {message && <div className="bg-green-100 text-green-700 px-3 py-2 rounded text-sm">{message}</div>}

          <div className="flex items-center justify-between">
            <span>Recibir alertas</span>
            <input type="checkbox" checked={alertsActive} onChange={(e) => setAlertsActive(e.target.checked)} />
          </div>

          <div>
            <label className="block text-sm font-bold mb-1">Radio: {radiusKm} km</label>
            <input
              type="range"
              min={1}
              max={20}
              value={radiusKm}
              onChange={(e) => setRadiusKm(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <div className="flex items-center justify-between">
            <span>Push</span>
            <input type="checkbox" checked={pushEnabled} onChange={(e) => setPushEnabled(e.target.checked)} />
          </div>
          <div className="flex items-center justify-between">
            <span>SMS</span>
            <input type="checkbox" checked={smsEnabled} onChange={(e) => setSmsEnabled(e.target.checked)} />
          </div>
          <div className="flex items-center justify-between">
            <span>Email</span>
            <input type="checkbox" checked={emailEnabled} onChange={(e) => setEmailEnabled(e.target.checked)} />
          </div>

          <button className="btn btn-primary w-full" onClick={handleSavePreferences}>
            Guardar Preferencias
          </button>

          {preferences?.latitude == null && (
            <p className="text-gray-400 text-xs">
              Nota: define tu ubicación desde un reporte o avistamiento para recibir alertas por radio.
            </p>
          )}
        </div>
      </main>
    </div>
  )
}
