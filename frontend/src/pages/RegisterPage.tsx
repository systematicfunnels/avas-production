import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '@/services/api'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '', full_name: '', organization: '' })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    try {
      await api.register(form.email, form.password, form.full_name, form.organization || undefined)
      await login(form.email, form.password)
      toast.success('Account created!')
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setError('')
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center font-bold text-xl mx-auto mb-4">AV</div>
          <h1 className="text-2xl font-bold text-white">Create your account</h1>
          <p className="text-gray-400 text-sm mt-1">Start inspecting infrastructure with AI</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-red-400 text-sm">{error}</div>
          )}
          {[
            { label: 'Full Name', field: 'full_name', type: 'text', placeholder: 'Jane Smith', required: true },
            { label: 'Email', field: 'email', type: 'email', placeholder: 'you@company.com', required: true },
            { label: 'Organization', field: 'organization', type: 'text', placeholder: 'Acme Infrastructure (optional)', required: false },
            { label: 'Password', field: 'password', type: 'password', placeholder: '8+ chars, 1 uppercase, 1 number', required: true },
          ].map(({ label, field, type, placeholder, required }) => (
            <div key={field}>
              <label className="block text-sm text-gray-400 mb-1.5">{label}</label>
              <input
                type={type}
                required={required}
                value={form[field as keyof typeof form]}
                onChange={update(field)}
                placeholder={placeholder}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
          ))}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {isLoading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-gray-500 text-sm mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
