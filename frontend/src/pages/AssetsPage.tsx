import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '@/services/api'
import toast from 'react-hot-toast'
import type { AssetCreate } from '@/types'

const ASSET_TYPES = ['Solar Farm', 'Wind Turbine', 'Bridge', 'Pipeline', 'Building', 'Road', 'Electrical Tower', 'Other']

export function AssetsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<AssetCreate>({ name: '', asset_type: '' })

  const { data: assets, isLoading } = useQuery('assets', api.listAssets.bind(api))

  const createMutation = useMutation(
    (payload: AssetCreate) => api.createAsset(payload),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('assets')
        toast.success('Asset created')
        setShowForm(false)
        setForm({ name: '', asset_type: '' })
      },
      onError: (err: any) => toast.error(err.response?.data?.detail || 'Failed to create asset'),
    }
  )

  const handleCreate = () => {
    if (!form.name.trim()) { toast.error('Asset name is required'); return }
    if (!form.asset_type) { toast.error('Asset type is required'); return }
    createMutation.mutate(form)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Assets</h1>
          <p className="text-gray-400 text-sm mt-1">Infrastructure assets under monitoring</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
        >
          + Add Asset
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 space-y-4">
          <h3 className="text-white font-semibold">New Asset</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Name *</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g., Solar Array Block A"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Type *</label>
              <select
                value={form.asset_type}
                onChange={(e) => setForm({ ...form, asset_type: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="">Select type</option>
                {ASSET_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Location</label>
              <input
                value={form.location_name || ''}
                onChange={(e) => setForm({ ...form, location_name: e.target.value })}
                placeholder="e.g., Arizona, USA"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <input
                value={form.description || ''}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Optional"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button onClick={handleCreate} disabled={createMutation.isLoading} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
              {createMutation.isLoading ? 'Creating…' : 'Create Asset'}
            </button>
            <button onClick={() => setShowForm(false)} className="bg-gray-800 text-gray-300 text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl h-32 animate-pulse" />)}
        </div>
      ) : !assets || assets.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-16 text-center">
          <div className="text-4xl mb-4">🏗️</div>
          <h3 className="text-white font-semibold mb-2">No assets yet</h3>
          <p className="text-gray-400 text-sm">Add infrastructure assets to track their inspection history and risk scores.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {assets.map((asset) => (
            <div key={asset.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-white font-medium">{asset.name}</h3>
                  <span className="text-xs text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded-full mt-1 inline-block">
                    {asset.asset_type}
                  </span>
                </div>
                <div className={`text-lg font-bold ${
                  asset.risk_score >= 80 ? 'text-red-400' :
                  asset.risk_score >= 60 ? 'text-orange-400' :
                  asset.risk_score >= 40 ? 'text-yellow-400' : 'text-green-400'
                }`}>
                  {asset.risk_score.toFixed(0)}
                </div>
              </div>
              {asset.location_name && (
                <p className="text-gray-500 text-sm">📍 {asset.location_name}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
