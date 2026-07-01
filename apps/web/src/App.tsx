import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import PrivateRoute from './auth/PrivateRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ReportLostPet from './pages/ReportLostPet'
import SightingForm from './pages/SightingForm'
import ImageSearch from './pages/ImageSearch'
import CaregiverNetwork from './pages/CaregiverNetwork'
import Notifications from './pages/Notifications'

export default function App() {
  const { isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Cargando...</div>
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* RF 1.3 / RF 2.1: sighting reports and image search allow anonymous citizens */}
        <Route path="/sighting" element={<SightingForm />} />
        <Route path="/search" element={<ImageSearch />} />

        <Route element={<PrivateRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/report-lost-pet" element={<ReportLostPet />} />
          <Route path="/caregivers" element={<CaregiverNetwork />} />
          <Route path="/notifications" element={<Notifications />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}
