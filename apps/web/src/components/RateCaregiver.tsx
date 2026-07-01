import { useState } from 'react'
import * as caregiversApi from '../api/caregivers'

interface RateCaregiverProps {
  caregiverId: string
  onRated?: () => void
}

export default function RateCaregiver({ caregiverId, onRated }: RateCaregiverProps) {
  const [open, setOpen] = useState(false)
  const [reportId, setReportId] = useState('')
  const [score, setScore] = useState(5)
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    setError('')
    if (!reportId.trim()) {
      setError('Ingresa el ID del reporte donde este cuidador te ayudó')
      return
    }
    try {
      await caregiversApi.addRating(caregiverId, { score, comment: comment || undefined, report_id: reportId })
      setSubmitted(true)
      onRated?.()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al enviar la calificación')
    }
  }

  if (!open) {
    return (
      <button className="btn btn-secondary w-full mt-2" onClick={() => setOpen(true)}>
        Calificar
      </button>
    )
  }

  if (submitted) {
    return <p className="text-green-600 text-sm mt-2">¡Gracias por tu reseña!</p>
  }

  return (
    <div className="mt-3 space-y-2 border-t pt-3">
      {error && <p className="text-red-600 text-sm">{error}</p>}

      <input
        className="input"
        placeholder="ID del reporte donde te ayudó"
        value={reportId}
        onChange={(e) => setReportId(e.target.value)}
      />

      <select className="input" value={score} onChange={(e) => setScore(Number(e.target.value))}>
        {[5, 4, 3, 2, 1].map((n) => (
          <option key={n} value={n}>
            {'★'.repeat(n)} ({n})
          </option>
        ))}
      </select>

      <textarea
        className="input"
        rows={2}
        placeholder="Comentario (opcional)"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />

      <div className="flex gap-2">
        <button className="btn btn-primary flex-1" onClick={handleSubmit}>
          Enviar
        </button>
        <button className="btn btn-secondary" onClick={() => setOpen(false)}>
          Cancelar
        </button>
      </div>
    </div>
  )
}
