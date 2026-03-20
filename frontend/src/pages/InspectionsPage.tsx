import { useState } from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import { formatDistanceToNow } from 'date-fns'
import type { InspectionListItem } from '@/types'

const STATUS_COLORS: Record<string, string> = {
  pending: 'text-gray-400 bg-gray-500/20',
  processing: 'text-blue-400 bg-blue-500/20',
  completed: 'text-green-400 bg-green-500/20',
  failed: 'text-red-400 bg-red-500/20',
}

export function InspectionsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const { data, isLoading } = useQuery(['inspections', page], () => api.listInspections(page, 20))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Inspections</h1>
          <p className="text-gray-400 text-sm mt-1">{data?.total ?? 0} total inspections</p>
        </div>
        <button
          onClick={() => navigate('/inspections/new')}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
        >
          + New Inspection
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl h-20 animate-pulse" />
          ))}
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-16 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-white font-semibold mb-2">No inspections yet</h3>
          <p className="text-gray-400 text-sm mb-6">Create your first inspection to start detecting defects.</p>
          <button onClick={() => navigate('/inspections/new')} className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium">
            Start First Inspection
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {data.items.map((inspection: InspectionListItem) => (
              <div
                key={inspection.id}
                onClick={() => navigate(`/inspections/${inspection.id}`)}
                className="bg-gray-900 border border-gray-800 rounded-xl p-5 cursor-pointer hover:border-gray-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_COLORS[inspection.status]}`}>
                        {inspection.status}
                      </span>
                      <h3 className="text-white font-medium truncate">{inspection.title}</h3>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{inspection.image_count} images</span>
                      {inspection.defect_count > 0 && (
                        <span className="text-orange-400">{inspection.defect_count} defects</span>
                      )}
                      <span>{formatDistanceToNow(new Date(inspection.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                  {inspection.risk_score != null && (
                    <div className="text-right ml-4">
                      <div className={`text-lg font-bold ${
                        inspection.risk_score >= 80 ? 'text-red-400' :
                        inspection.risk_score >= 60 ? 'text-orange-400' :
                        inspection.risk_score >= 40 ? 'text-yellow-400' : 'text-green-400'
                      }`}>
                        {inspection.risk_score.toFixed(0)}
                      </div>
                      <div className="text-xs text-gray-500">risk</div>
                    </div>
                  )}
                  <span className="text-gray-600 ml-4">›</span>
                </div>
              </div>
            ))}
          </div>

          {data.pages > 1 && (
            <div className="flex justify-center gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                className="px-4 py-2 bg-gray-900 border border-gray-700 text-gray-300 rounded-lg text-sm disabled:opacity-40"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-gray-400 text-sm">Page {page} of {data.pages}</span>
              <button
                disabled={page === data.pages}
                onClick={() => setPage((p) => p + 1)}
                className="px-4 py-2 bg-gray-900 border border-gray-700 text-gray-300 rounded-lg text-sm disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
