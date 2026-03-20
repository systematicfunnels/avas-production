import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import toast from 'react-hot-toast'

const MAX_FILES = 50
const MAX_SIZE_MB = 50
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/tiff', 'image/webp']

export function NewInspectionPage() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [assetId, setAssetId] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [step, setStep] = useState<'form' | 'uploading' | 'analyzing'>('form')

  const { data: assets } = useQuery('assets', api.listAssets.bind(api))

  const onDrop = useCallback((accepted: File[], rejected: any[]) => {
    if (rejected.length > 0) {
      toast.error(`${rejected.length} file(s) rejected — check type and size limits`)
    }
    setFiles((prev) => {
      const combined = [...prev, ...accepted]
      if (combined.length > MAX_FILES) {
        toast.error(`Maximum ${MAX_FILES} images per inspection`)
        return prev
      }
      return combined
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/jpeg': [], 'image/png': [], 'image/tiff': [], 'image/webp': [] },
    maxSize: MAX_SIZE_MB * 1024 * 1024,
    multiple: true,
  })

  const removeFile = (idx: number) => setFiles((prev) => prev.filter((_, i) => i !== idx))

  const handleSubmit = async () => {
    if (!title.trim()) { toast.error('Please enter an inspection title'); return }
    if (files.length === 0) { toast.error('Please upload at least one image'); return }

    setIsSubmitting(true)
    setStep('uploading')

    try {
      const inspection = await api.createInspection(title.trim(), assetId || undefined)
      await api.uploadImages(inspection.id, files, setUploadProgress)

      setStep('analyzing')
      await api.analyzeInspection(inspection.id)

      toast.success('Inspection submitted for AI analysis!')
      navigate(`/inspections/${inspection.id}`)
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to submit inspection'
      toast.error(msg)
      setStep('form')
      setIsSubmitting(false)
    }
  }

  if (step === 'uploading' || step === 'analyzing') {
    return (
      <div className="max-w-lg mx-auto mt-24 text-center">
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-12">
          <div className="text-5xl mb-6">{step === 'uploading' ? '⬆️' : '🤖'}</div>
          <h2 className="text-xl font-semibold text-white mb-2">
            {step === 'uploading' ? 'Uploading images…' : 'AI Analysis in progress…'}
          </h2>
          <p className="text-gray-400 text-sm mb-6">
            {step === 'uploading'
              ? `${uploadProgress}% complete`
              : 'Our AI is detecting defects and computing risk scores. This may take a few minutes.'}
          </p>
          {step === 'uploading' && (
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          )}
          {step === 'analyzing' && (
            <div className="flex justify-center">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">New Inspection</h1>
        <p className="text-gray-400 text-sm mt-1">Upload inspection images for AI defect analysis</p>
      </div>

      <div className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Inspection Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Solar Array Block A — March 2026"
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Asset */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Link to Asset (optional)</label>
          <select
            value={assetId}
            onChange={(e) => setAssetId(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option value="">— No asset —</option>
            {assets?.map((a) => (
              <option key={a.id} value={a.id}>{a.name} ({a.asset_type})</option>
            ))}
          </select>
        </div>

        {/* Drop zone */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Inspection Images * <span className="text-gray-500">({files.length}/{MAX_FILES})</span>
          </label>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-blue-500 bg-blue-500/5' : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-3xl mb-3">📸</div>
            <p className="text-white font-medium">Drop images here or click to browse</p>
            <p className="text-gray-400 text-sm mt-1">JPEG, PNG, TIFF, WebP — up to {MAX_SIZE_MB}MB per file</p>
          </div>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 max-h-48 overflow-y-auto">
            <div className="space-y-2">
              {files.map((f, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-300 truncate max-w-xs">{f.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-gray-500">{(f.size / 1024 / 1024).toFixed(1)} MB</span>
                    <button onClick={() => removeFile(i)} className="text-gray-600 hover:text-red-400 transition-colors">✕</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || !title.trim() || files.length === 0}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {isSubmitting ? 'Processing…' : `Run AI Analysis (${files.length} image${files.length !== 1 ? 's' : ''})`}
        </button>
      </div>
    </div>
  )
}
