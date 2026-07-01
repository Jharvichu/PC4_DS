import { useRef, useState } from 'react'

interface ImageUploadProps {
  onChange: (dataUrl: string) => void
  label?: string
}

const ACCEPTED_TYPES = ['image/jpeg', 'image/png']

export default function ImageUpload({ onChange, label = 'Foto' }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (file: File | undefined) => {
    setError(null)

    if (!file) return

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Solo se aceptan imágenes JPEG o PNG')
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const dataUrl = reader.result as string
      setPreview(dataUrl)
      onChange(dataUrl)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div>
      <label className="block text-gray-700 text-sm font-bold mb-2">{label}</label>

      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
        onClick={() => inputRef.current?.click()}
      >
        {preview ? (
          <img src={preview} alt="preview" className="mx-auto max-h-48 rounded" />
        ) : (
          <p className="text-gray-500">Haz clic para subir una imagen (JPEG/PNG)</p>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}
    </div>
  )
}
