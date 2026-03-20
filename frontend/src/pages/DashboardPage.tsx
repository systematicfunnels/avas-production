import { useQuery } from 'react-query'
import { api } from '@/services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import type { RiskSummary } from '@/types'

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${color || 'text-white'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

function RiskBar({ score }: { score: number }) {
  const color = score >= 80 ? '#ef4444' : score >= 60 ? '#f97316' : score >= 40 ? '#eab308' : '#22c55e'
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-gray-800 rounded-full h-2">
        <div className="h-2 rounded-full transition-all" style={{ width: `${score}%`, backgroundColor: color }} />
      </div>
      <span className="text-sm font-medium w-10 text-right" style={{ color }}>{score.toFixed(0)}</span>
    </div>
  )
}

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboard-stats', api.getDashboardStats.bind(api))
  const { data: risks, isLoading: risksLoading } = useQuery('risk-summary', api.getRiskSummary.bind(api))

  if (statsLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5 h-24 animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  const riskChartData = risks?.slice(0, 10).map((r: RiskSummary) => ({
    name: r.asset_name.length > 15 ? r.asset_name.slice(0, 15) + '…' : r.asset_name,
    score: r.risk_score,
    defects: r.defect_count,
  })) || []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Infrastructure Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">AI-powered inspection intelligence overview</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard label="Total Inspections" value={stats.total_inspections} />
          <StatCard label="Assets Monitored" value={stats.total_assets} />
          <StatCard label="Total Defects" value={stats.total_defects} />
          <StatCard label="Critical Defects" value={stats.critical_defects} color="text-red-400" sub="Requires immediate action" />
          <StatCard label="Avg Risk Score" value={`${stats.avg_risk_score.toFixed(1)}`} sub="Out of 100" />
          <StatCard label="This Month" value={stats.inspections_this_month} sub="Inspections" />
        </div>
      )}

      {/* Risk chart */}
      {risks && risks.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-4">Asset Risk Scores</h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={riskChartData} margin={{ top: 4, right: 4, left: -20, bottom: 40 }}>
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                  labelStyle={{ color: '#f9fafb' }}
                />
                <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                  {riskChartData.map((entry, i) => (
                    <Cell
                      key={i}
                      fill={entry.score >= 80 ? '#ef4444' : entry.score >= 60 ? '#f97316' : entry.score >= 40 ? '#eab308' : '#22c55e'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-4">Maintenance Priority List</h2>
            <div className="space-y-3">
              {risks.slice(0, 8).map((r: RiskSummary) => (
                <div key={r.asset_id}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-300 truncate max-w-[200px]">{r.asset_name}</span>
                    <span className="text-xs text-gray-500">{r.defect_count} defects</span>
                  </div>
                  <RiskBar score={r.risk_score} />
                </div>
              ))}
              {risks.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-8">No assets with inspections yet</p>
              )}
            </div>
          </div>
        </div>
      )}

      {(!stats || stats.total_inspections === 0) && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-white font-semibold mb-2">No inspections yet</h3>
          <p className="text-gray-400 text-sm">Upload your first inspection images to get started with AI defect detection.</p>
        </div>
      )}
    </div>
  )
}
