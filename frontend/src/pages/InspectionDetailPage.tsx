import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { api } from '@/services/api'
import type { Defect } from '@/types'

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  low: 'bg-green-500/20 text-green-400 border-green-500/30',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-500/20 text-gray-400',
  processing: 'bg-blue-500/20 text-blue-400',
  completed: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
}

function RiskGauge({ score }: { score: number }) {
  const color = score >= 80 ? '#ef4444' : score >= 60 ? '#f97316' : score >= 40 ? '#eab308' : '#22c55e'
  const label = score >= 80 ? 'Critical' : score >= 60 ? 'High' : score >= 40 ? 'Medium' : 'Low'
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-24 h-24">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#1f2937" strokeWidth="10" />
          <circle
            cx="50" cy="50" r="40" fill="none"
            stroke={color} strokeWidth="10"
            strokeDasharray={`${(score / 100) * 251} 251`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-white">{score.toFixed(0)}</span>
        </div>
      </div>
      <span className="text-sm font-medium" style={{ color }}>{label} Risk</span>
    </div>
  )
}

export function InspectionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: inspection, isLoading, refetch } = useQuery(
    ['inspection', id],
    () => api.getInspection(id!),
    {
      refetchInterval: (data) =>
        data?.status === 'processing' || data?.status === 'pending' ? 3000 : false,
    }
  )

  if (isLoading) {
    return <div className="flex justify-center mt-24"><div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" /></div>
  }

  if (!inspection) return <div className="text-gray-400">Inspection not found</div>

  const criticalCount = inspection.defects.filter((d) => d.severity === 'critical').length
  const highCount = inspection.defects.filter((d) => d.severity === 'high').length

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{inspection.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[inspection.status]}`}>
              {inspection.status.toUpperCase()}
            </span>
            <span className="text-gray-500 text-sm">{inspection.image_count} images</span>
            {inspection.processing_duration_ms && (
              <span className="text-gray-500 text-sm">
                Processed in {(inspection.processing_duration_ms / 1000).toFixed(1)}s
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Processing state */}
      {(inspection.status === 'processing' || inspection.status === 'pending') && (
        <div className="bg-blue-600/10 border border-blue-600/20 rounded-xl p-6 flex items-center gap-4">
          <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin flex-shrink-0" />
          <div>
            <p className="text-blue-400 font-medium">AI analysis in progress</p>
            <p className="text-blue-400/70 text-sm">This page will auto-refresh when complete.</p>
          </div>
        </div>
      )}

      {/* Failed state */}
      {inspection.status === 'failed' && (
        <div className="bg-red-600/10 border border-red-600/20 rounded-xl p-6">
          <p className="text-red-400 font-medium">Analysis failed</p>
          <p className="text-red-400/70 text-sm mt-1">{inspection.error_message || 'Unknown error'}</p>
        </div>
      )}

      {/* Completed results */}
      {inspection.status === 'completed' && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col items-center justify-center">
              {inspection.risk_score != null && <RiskGauge score={inspection.risk_score} />}
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <p className="text-gray-400 text-sm">Total Defects</p>
              <p className="text-3xl font-bold text-white mt-1">{inspection.defect_count}</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <p className="text-gray-400 text-sm">Critical</p>
              <p className={`text-3xl font-bold mt-1 ${criticalCount > 0 ? 'text-red-400' : 'text-white'}`}>{criticalCount}</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <p className="text-gray-400 text-sm">High Severity</p>
              <p className={`text-3xl font-bold mt-1 ${highCount > 0 ? 'text-orange-400' : 'text-white'}`}>{highCount}</p>
            </div>
          </div>

          {/* Defects list */}
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">Detected Defects</h2>
            {inspection.defects.length === 0 ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-10 text-center">
                <div className="text-3xl mb-3">✅</div>
                <p className="text-white font-medium">No defects detected</p>
                <p className="text-gray-400 text-sm mt-1">Infrastructure appears to be in good condition.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {inspection.defects
                  .sort((a, b) => {
                    const order = { critical: 0, high: 1, medium: 2, low: 3 }
                    return (order[a.severity] ?? 4) - (order[b.severity] ?? 4)
                  })
                  .map((defect: Defect) => (
                    <div key={defect.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${SEVERITY_COLORS[defect.severity]}`}>
                              {defect.severity.toUpperCase()}
                            </span>
                            <span className="text-white font-medium capitalize">
                              {defect.defect_type.replace(/_/g, ' ')}
                            </span>
                            <span className="text-gray-500 text-sm">
                              {(defect.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                          {defect.description && (
                            <p className="text-gray-400 text-sm mb-2">{defect.description}</p>
                          )}
                          {defect.recommendation && (
                            <div className="bg-gray-800 rounded-lg px-3 py-2 mt-2">
                              <p className="text-xs text-gray-400 font-medium mb-0.5">Recommendation</p>
                              <p className="text-gray-300 text-sm">{defect.recommendation}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
