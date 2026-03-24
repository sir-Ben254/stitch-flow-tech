'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { 
  Upload, FileImage, Download, Wallet, CreditCard, 
  Clock, Check, X, RefreshCw, Loader2, Trash2, 
  Eye, Zap, AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

// Types
interface Job {
  id: string
  filename: string
  status: string
  complexity: string
  price: number
  payment_status: string
  created_at: string
  output_dst_url?: string
  output_svg_url?: string
  output_json_url?: string
}

interface WalletData {
  balance: number
  currency: string
}

// API Base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('upload')
  const [jobs, setJobs] = useState<Job[]>([])
  const [wallet, setWallet] = useState<WalletData>({ balance: 0, currency: 'KES' })
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [processingJob, setProcessingJob] = useState<string | null>(null)

  // Check auth (simplified)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [phone, setPhone] = useState('')

  useEffect(() => {
    // Check if user is logged in (simplified)
    const token = localStorage.getItem('access_token')
    if (token) {
      setIsAuthenticated(true)
      fetchJobs()
      fetchWallet()
    }
  }, [])

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API_URL}/jobs/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setJobs(data)
      }
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    }
  }

  const fetchWallet = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API_URL}/wallet/balance`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setWallet(data)
      }
    } catch (error) {
      console.error('Failed to fetch wallet:', error)
    }
  }

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!isAuthenticated) {
      toast.error('Please login first')
      return
    }

    for (const file of acceptedFiles) {
      setUploading(true)
      
      try {
        const token = localStorage.getItem('access_token')
        const formData = new FormData()
        formData.append('file', file)
        formData.append('complexity', 'auto')
        formData.append('captcha_token', 'demo') // Simplified for demo

        const res = await fetch(`${API_URL}/jobs/upload`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        })

        if (res.ok) {
          const data = await res.json()
          setProcessingJob(data.job_id)
          toast.success('Image uploaded! Processing started.')
          fetchJobs()
        } else {
          toast.error('Upload failed')
        }
      } catch (error) {
        console.error('Upload error:', error)
        toast.error('Upload failed')
      } finally {
        setUploading(false)
      }
    }
  }, [isAuthenticated])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    },
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  const handlePayment = async (jobId: string, method: 'stk' | 'wallet') => {
    if (!phone) {
      toast.error('Please enter your phone number')
      return
    }

    setLoading(true)
    try {
      if (method === 'wallet') {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API_URL}/wallet/pay/${jobId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (res.ok) {
          toast.success('Payment successful!')
          fetchWallet()
          fetchJobs()
        } else {
          const data = await res.json()
          toast.error(data.detail || 'Payment failed')
        }
      } else {
        const token = localStorage.getItem('access_token')
        const res = await fetch(`${API_URL}/payments/stkpush`, {
          method: 'POST',
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ job_id: jobId, phone })
        })
        
        if (res.ok) {
          toast.success('STK Push sent! Check your phone.')
        } else {
          toast.error('Payment initiation failed')
        }
      }
    } catch (error) {
      console.error('Payment error:', error)
      toast.error('Payment failed')
    } finally {
      setLoading(false)
    }
  }

  const handleTopup = async () => {
    if (!phone) {
      toast.error('Please enter your phone number')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`${API_URL}/wallet/topup`, {
        method: 'POST',
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount: 500, phone }) // Default 500 KES
      })
      
      if (res.ok) {
        toast.success('STK Push sent! Check your phone.')
      } else {
        toast.error('Top-up failed')
      }
    } catch (error) {
      console.error('Topup error:', error)
      toast.error('Top-up failed')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-500'
      case 'processing': return 'text-yellow-500'
      case 'failed': return 'text-red-500'
      default: return 'text-slate-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <Check size={16} />
      case 'processing': return <RefreshCw size={16} className="animate-spin" />
      case 'failed': return <X size={16} />
      default: return <Clock size={16} />
    }
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className="w-64 bg-surface border-r border-surface-light p-6 hidden md:block">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <FileImage className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-heading font-bold">StitchFlow</span>
        </div>

        <nav className="space-y-2">
          {[
            { id: 'upload', label: 'Upload', icon: Upload },
            { id: 'jobs', label: 'My Jobs', icon: FileImage },
            { id: 'wallet', label: 'Wallet', icon: Wallet },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                activeTab === item.id 
                  ? 'bg-primary/20 text-primary' 
                  : 'text-slate-400 hover:bg-surface-light'
              }`}
            >
              <item.icon size={20} />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400">Balance</span>
              <Wallet size={18} className="text-accent" />
            </div>
            <div className="text-2xl font-heading font-bold">
              {wallet.currency} {wallet.balance.toFixed(2)}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto">
        {/* Mobile Header */}
        <div className="md:hidden flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <FileImage className="w-4 h-4 text-white" />
            </div>
            <span className="font-heading font-bold">StitchFlow</span>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">Balance</div>
            <div className="font-bold">KES {wallet.balance.toFixed(2)}</div>
          </div>
        </div>

        {/* Mobile Nav */}
        <div className="md:hidden flex gap-2 mb-6 overflow-x-auto pb-2">
          {['upload', 'jobs', 'wallet'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap ${
                activeTab === tab ? 'bg-primary text-white' : 'bg-surface text-slate-400'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-2xl font-heading font-bold mb-6">Upload Image</h1>
            
            <div 
              {...getRootProps()} 
              className={`upload-zone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="w-16 h-16 mx-auto mb-4 text-primary" />
              {isDragActive ? (
                <p className="text-lg">Drop the file here...</p>
              ) : (
                <>
                  <p className="text-lg mb-2">Drag & drop your image here</p>
                  <p className="text-slate-400">or click to browse</p>
                  <p className="text-sm text-slate-500 mt-4">PNG, JPG, JPEG, WebP, BMP - Max 10MB</p>
                </>
              )}
            </div>

            {uploading && (
              <div className="mt-6 flex items-center gap-4">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
                <span>Uploading and processing...</span>
              </div>
            )}

            {/* Phone Input for Payments */}
            <div className="mt-8 card">
              <h3 className="font-heading font-semibold mb-4">Payment Phone Number</h3>
              <p className="text-sm text-slate-400 mb-4">Enter your M-Pesa registered number for STK Push payments</p>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="254700000000"
                className="input"
              />
            </div>
          </motion.div>
        )}

        {/* Jobs Tab */}
        {activeTab === 'jobs' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-heading font-bold">My Jobs</h1>
              <button 
                onClick={fetchJobs}
                className="p-2 hover:bg-surface-light rounded-lg transition-colors"
              >
                <RefreshCw size={20} />
              </button>
            </div>

            {jobs.length === 0 ? (
              <div className="text-center py-12">
                <FileImage className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                <p className="text-slate-400">No jobs yet. Upload an image to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.id} className="card flex flex-col md:flex-row md:items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <FileImage className="w-5 h-5 text-primary" />
                        <span className="font-semibold">{job.filename}</span>
                        <span className={`flex items-center gap-1 text-sm ${getStatusColor(job.status)}`}>
                          {getStatusIcon(job.status)}
                          {job.status}
                        </span>
                      </div>
                      <div className="flex gap-4 text-sm text-slate-400">
                        <span>Complexity: {job.complexity}</span>
                        <span>KES {job.price}</span>
                        <span className={job.payment_status === 'paid' ? 'text-green-500' : 'text-yellow-500'}>
                          {job.payment_status === 'paid' ? 'Paid' : 'Unpaid'}
                        </span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {job.status === 'completed' && job.payment_status === 'paid' && (
                        <div className="flex gap-2">
                          {job.output_dst_url && (
                            <a 
                              href={job.output_dst_url} 
                              download
                              className="btn-secondary py-2 px-4 text-sm flex items-center gap-2"
                            >
                              <Download size={16} /> DST
                            </a>
                          )}
                          {job.output_svg_url && (
                            <a 
                              href={job.output_svg_url} 
                              download
                              className="btn-secondary py-2 px-4 text-sm flex items-center gap-2"
                            >
                              <Download size={16} /> SVG
                            </a>
                          )}
                          {job.output_json_url && (
                            <a 
                              href={job.output_json_url} 
                              download
                              className="btn-secondary py-2 px-4 text-sm flex items-center gap-2"
                            >
                              <Download size={16} /> JSON
                            </a>
                          )}
                        </div>
                      )}

                      {job.payment_status !== 'paid' && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handlePayment(job.id, 'wallet')}
                            disabled={loading || wallet.balance < job.price}
                            className="btn-primary py-2 px-4 text-sm flex items-center gap-2 disabled:opacity-50"
                          >
                            <Wallet size={16} /> Pay Wallet
                          </button>
                          <button
                            onClick={() => handlePayment(job.id, 'stk')}
                            disabled={loading}
                            className="btn-secondary py-2 px-4 text-sm flex items-center gap-2"
                          >
                            <CreditCard size={16} /> M-Pesa
                          </button>
                        </div>
                      )}

                      {job.status === 'processing' && (
                        <div className="flex items-center gap-2 text-yellow-500">
                          <RefreshCw size={16} className="animate-spin" />
                          Processing...
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Wallet Tab */}
        {activeTab === 'wallet' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-2xl font-heading font-bold mb-6">Wallet</h1>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center">
                    <Wallet className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <div className="text-slate-400">Available Balance</div>
                    <div className="text-3xl font-heading font-bold">
                      KES {wallet.balance.toFixed(2)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleTopup}
                  disabled={loading || !phone}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="animate-spin" size={20} /> : <Zap size={20} />}
                  Top Up via M-Pesa
                </button>
              </div>

              <div className="card">
                <h3 className="font-heading font-semibold mb-4">Quick Top Up</h3>
                <div className="grid grid-cols-3 gap-3">
                  {[100, 250, 500, 1000, 2000, 5000].map(amount => (
                    <button
                      key={amount}
                      onClick={async () => {
                        if (!phone) {
                          toast.error('Enter phone number first')
                          return
                        }
                        setLoading(true)
                        try {
                          const token = localStorage.getItem('access_token')
                          const res = await fetch(`${API_URL}/wallet/topup`, {
                            method: 'POST',
                            headers: { 
                              Authorization: `Bearer ${token}`,
                              'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ amount, phone })
                          })
                          if (res.ok) toast.success('STK sent!')
                          else toast.error('Failed')
                        } catch {
                          toast.error('Failed')
                        } finally {
                          setLoading(false)
                        }
                      }}
                      disabled={loading}
                      className="py-3 bg-surface-light rounded-lg hover:bg-primary/20 transition-colors font-semibold"
                    >
                      KES {amount}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Info */}
            <div className="card bg-yellow-500/10 border-yellow-500/30">
              <div className="flex gap-3">
                <AlertCircle className="w-6 h-6 text-yellow-500 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">How it works</h3>
                  <p className="text-sm text-slate-400">
                    Click "Top Up" or select an amount above. You'll receive an M-Pesa STK push prompt. 
                    Enter your PIN to complete the payment. Your wallet will be credited instantly.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  )
}

// Login Page Component
function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      })

      if (res.ok) {
        const data = await res.json()
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        toast.success('Logged in successfully!')
        onLogin()
      } else {
        toast.error('Login failed. Check your credentials.')
      }
    } catch (error) {
      console.error('Login error:', error)
      toast.error('Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4">
            <FileImage className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-heading font-bold">Welcome Back</h1>
          <p className="text-slate-400 mt-2">Login to access your dashboard</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" size={20} /> : 'Login'}
          </button>
        </form>

        <p className="text-center text-slate-400 mt-6">
          Demo: Use registered credentials to login
        </p>
      </motion.div>
    </div>
  )
}
