import React, { useState, useEffect } from 'react'
import axios from '../services/axios'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'
import {
  Upload,
  Download,
  Play,
  Settings,
  Eye,
  FileText,
  AlertCircle,
  Check,
  X,
  Plus,
  Save
} from 'lucide-react'
import TextDiff from '../components/TextDiff'
import MetricsDisplay from '../components/MetricsDisplay'

const Editor = () => {
  const [inputText, setInputText] = useState('')
  const [outputText, setOutputText] = useState('')
  const [processing, setProcessing] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [changes, setChanges] = useState([])
  const [viewMode, setViewMode] = useState('side-by-side')
  const [integrityMode, setIntegrityMode] = useState('editor')
  const [styleProfiles, setStyleProfiles] = useState([])
  const [selectedProfile, setSelectedProfile] = useState(null)

  const [parameters, setParameters] = useState({
    tone: 'neutral',
    formality: 0.5,
    burstiness: 0.5,
    perplexity_target: 50,
    idiom_density: 0.3,
    conciseness: 0.5,
    temperature: 0.7,
    seed: null,
    preserve_citations: true,
    preserve_quotes: true,
    keep_language: true,
    max_tokens: null,
    style_profile_id: null
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        const formData = new FormData()
        formData.append('file', file)

        try {
          const response = await axios.post('/api/upload', formData)
          setInputText(response.data.text)
          toast.success('File uploaded successfully')
        } catch (error) {
          toast.error('Failed to upload file')
        }
      }
    }
  })

  useEffect(() => {
    fetchStyleProfiles()
  }, [])

  const fetchStyleProfiles = async () => {
    try {
      const response = await axios.get('/api/style-profiles')
      setStyleProfiles(response.data)
    } catch (error) {
      console.error('Failed to fetch style profiles:', error)
    }
  }

  const handleProfileSelect = (profileId) => {
    if (profileId === 'none') {
      setSelectedProfile(null)
      setParameters(prev => ({ ...prev, style_profile_id: null }))
    } else {
      const profile = styleProfiles.find(p => p.id === profileId)
      setSelectedProfile(profile)
      setParameters(prev => ({ ...prev, style_profile_id: profileId }))

      // Apply profile metrics as parameters if available
      if (profile?.metrics) {
        const metrics = profile.metrics
        setParameters(prev => ({
          ...prev,
          formality: metrics.formal_words || prev.formality,
          burstiness: Math.min(1, (metrics.sentence_length_variance || 10) / 20),
          conciseness: 1 - Math.min(1, (metrics.avg_sentence_length || 15) / 30)
        }))
      }

      toast.success(`Applied "${profile.name}" style profile`)
    }
  }

  const handleHumanize = async () => {
    if (!inputText.trim()) {
      toast.error('Please enter some text to humanize')
      return
    }

    setProcessing(true)
    setOutputText('')
    setMetrics(null)
    setChanges([])

    try {
      const response = await axios.post('/api/humanize', {
        text: inputText,
        ...parameters,
        integrity_mode: integrityMode
      })

      setJobId(response.data.job_id)
      pollJobStatus(response.data.job_id)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process text')
      setProcessing(false)
    }
  }

  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/job/${jobId}`)

        if (response.data.status === 'completed') {
          setOutputText(response.data.output_text)
          setMetrics(response.data.metrics)
          setChanges(response.data.changes || [])
          setProcessing(false)
          clearInterval(interval)
          toast.success('Text humanized successfully!')
        } else if (response.data.status === 'failed') {
          toast.error(response.data.error_message || 'Processing failed')
          setProcessing(false)
          clearInterval(interval)
        }
      } catch (error) {
        console.error('Polling error:', error)
        clearInterval(interval)
        setProcessing(false)
      }
    }, 2000)

    setTimeout(() => {
      clearInterval(interval)
      if (processing) {
        setProcessing(false)
        toast.error('Processing timeout')
      }
    }, 60000)
  }

  const handleDownload = () => {
    if (!outputText) return

    const blob = new Blob([outputText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'humanized_text.txt'
    a.click()
  }

  const handleSave = () => {
    if (!outputText) return

    const savedData = {
      original: inputText,
      humanized: outputText,
      metrics,
      parameters,
      timestamp: new Date().toISOString()
    }

    // Save to localStorage
    const savedItems = JSON.parse(localStorage.getItem('savedHumanizations') || '[]')
    savedItems.unshift(savedData)
    // Keep only last 10 saved items
    if (savedItems.length > 10) savedItems.pop()
    localStorage.setItem('savedHumanizations', JSON.stringify(savedItems))

    // Show success message
    alert('Humanized text saved successfully!')
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Text Humanizer</h1>

        <div className="flex items-center space-x-4">
          <select
            value={integrityMode}
            onChange={(e) => setIntegrityMode(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="editor">Editor Mode</option>
            <option value="academic">Academic Integrity Mode</option>
          </select>

          <button
            onClick={() => setViewMode(viewMode === 'side-by-side' ? 'diff' : 'side-by-side')}
            className="p-2 text-gray-600 hover:text-primary-600"
          >
            <Eye className="w-5 h-5" />
          </button>
        </div>
      </div>

      {integrityMode === 'academic' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
          <div>
            <h3 className="font-semibold text-yellow-800">Academic Integrity Mode Active</h3>
            <p className="text-sm text-yellow-700 mt-1">
              Citations and quotes will be preserved. Output will include invisible watermark for provenance tracking.
            </p>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Input Text</h2>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-4 mb-4 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600">
                {isDragActive
                  ? 'Drop the file here...'
                  : 'Drag & drop a file here, or click to select'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Supports TXT, DOCX, PDF (max 10MB)
              </p>
            </div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your text here..."
              className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />

            <div className="flex justify-between items-center mt-4">
              <span className="text-sm text-gray-500">
                {inputText.length} characters
              </span>
              <button
                onClick={handleHumanize}
                disabled={processing || !inputText.trim()}
                className="btn-primary flex items-center disabled:opacity-50"
              >
                {processing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Humanize
                  </>
                )}
              </button>
            </div>
          </div>

          {outputText && (
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Output</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={handleSave}
                    className="p-2 text-gray-600 hover:text-primary-600"
                    title="Save to browser"
                  >
                    <Save className="w-5 h-5" />
                  </button>
                  <button
                    onClick={handleDownload}
                    className="p-2 text-gray-600 hover:text-primary-600"
                    title="Download as TXT"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {viewMode === 'side-by-side' ? (
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Original</h3>
                    <div className="p-4 bg-gray-50 rounded-lg h-64 overflow-y-auto">
                      <p className="text-sm whitespace-pre-wrap">{inputText}</p>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Humanized</h3>
                    <div className="p-4 bg-green-50 rounded-lg h-64 overflow-y-auto">
                      <p className="text-sm whitespace-pre-wrap">{outputText}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <TextDiff original={inputText} humanized={outputText} />
              )}
            </div>
          )}

          {metrics && <MetricsDisplay metrics={metrics} />}
        </div>

        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Parameters
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Style Profile
                </label>
                <select
                  value={selectedProfile?.id || 'none'}
                  onChange={(e) => handleProfileSelect(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="none">None (Manual Settings)</option>
                  {styleProfiles.map(profile => (
                    <option key={profile.id} value={profile.id}>
                      {profile.name}
                    </option>
                  ))}
                </select>
                {selectedProfile && (
                  <p className="text-xs text-gray-500 mt-1">
                    {selectedProfile.description || 'Custom style profile'}
                  </p>
                )}
                <Link
                  to="/style-profiles"
                  className="flex items-center text-xs text-primary-600 hover:text-primary-700 mt-2"
                >
                  <Plus className="w-3 h-3 mr-1" />
                  Create new style profile
                </Link>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tone
                </label>
                <select
                  value={parameters.tone}
                  onChange={(e) => setParameters({ ...parameters, tone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="neutral">Neutral</option>
                  <option value="casual">Casual</option>
                  <option value="formal">Formal</option>
                  <option value="persuasive">Persuasive</option>
                  <option value="academic">Academic</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Formality: {parameters.formality}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parameters.formality}
                  onChange={(e) => setParameters({ ...parameters, formality: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Burstiness: {parameters.burstiness}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parameters.burstiness}
                  onChange={(e) => setParameters({ ...parameters, burstiness: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Perplexity Target: {parameters.perplexity_target}
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={parameters.perplexity_target}
                  onChange={(e) => setParameters({ ...parameters, perplexity_target: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Idiom Density: {parameters.idiom_density}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parameters.idiom_density}
                  onChange={(e) => setParameters({ ...parameters, idiom_density: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Conciseness: {parameters.conciseness}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parameters.conciseness}
                  onChange={(e) => setParameters({ ...parameters, conciseness: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {parameters.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={parameters.temperature}
                  onChange={(e) => setParameters({ ...parameters, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={parameters.preserve_citations}
                    onChange={(e) => setParameters({ ...parameters, preserve_citations: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm">Preserve Citations</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={parameters.preserve_quotes}
                    onChange={(e) => setParameters({ ...parameters, preserve_quotes: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm">Preserve Quotes</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={parameters.keep_language}
                    onChange={(e) => setParameters({ ...parameters, keep_language: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm">Keep Language</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Editor