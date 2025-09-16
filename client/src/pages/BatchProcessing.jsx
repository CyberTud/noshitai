import React, { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  Play,
  Pause,
  CheckCircle,
  XCircle,
  Clock,
  Download,
  Package
} from 'lucide-react'

const BatchProcessing = () => {
  const [files, setFiles] = useState([])
  const [processing, setProcessing] = useState(false)
  const [batchJobs, setBatchJobs] = useState([])
  const [parameters, setParameters] = useState({
    tone: 'neutral',
    formality: 0.5,
    preserve_citations: true,
    preserve_quotes: true
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024,
    multiple: true,
    onDrop: (acceptedFiles) => {
      const newFiles = acceptedFiles.map(file => ({
        id: Math.random().toString(36).substr(2, 9),
        file,
        name: file.name,
        size: file.size,
        status: 'pending',
        progress: 0
      }))
      setFiles([...files, ...newFiles])
      toast.success(`Added ${acceptedFiles.length} file(s) to queue`)
    }
  })

  const handleProcessBatch = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending')
    if (pendingFiles.length === 0) {
      toast.error('No pending files to process')
      return
    }

    setProcessing(true)

    for (const fileItem of pendingFiles) {
      try {
        setFiles(prev => prev.map(f =>
          f.id === fileItem.id ? { ...f, status: 'processing' } : f
        ))

        const formData = new FormData()
        formData.append('file', fileItem.file)
        const uploadResponse = await axios.post('/api/upload', formData)

        const humanizeResponse = await axios.post('/api/humanize', {
          text: uploadResponse.data.text,
          ...parameters
        })

        const jobId = humanizeResponse.data.job_id
        await pollJobCompletion(jobId, fileItem.id)

        setFiles(prev => prev.map(f =>
          f.id === fileItem.id ? { ...f, status: 'completed', jobId } : f
        ))

      } catch (error) {
        setFiles(prev => prev.map(f =>
          f.id === fileItem.id ? { ...f, status: 'failed', error: error.message } : f
        ))
      }
    }

    setProcessing(false)
    toast.success('Batch processing completed')
  }

  const pollJobCompletion = async (jobId, fileId) => {
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`/api/job/${jobId}`)

          if (response.data.status === 'completed') {
            clearInterval(interval)
            resolve(response.data)
          } else if (response.data.status === 'failed') {
            clearInterval(interval)
            reject(new Error(response.data.error_message))
          }
        } catch (error) {
          clearInterval(interval)
          reject(error)
        }
      }, 2000)

      setTimeout(() => {
        clearInterval(interval)
        reject(new Error('Processing timeout'))
      }, 60000)
    })
  }

  const handleDownloadAll = async () => {
    const completedFiles = files.filter(f => f.status === 'completed')
    if (completedFiles.length === 0) {
      toast.error('No completed files to download')
      return
    }

    for (const file of completedFiles) {
      if (file.jobId) {
        const response = await axios.get(`/api/job/${file.jobId}`)
        const blob = new Blob([response.data.output_text], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `humanized_${file.name}`
        a.click()
      }
    }
  }

  const handleRemoveFile = (id) => {
    setFiles(files.filter(f => f.id !== id))
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Batch Processing</h1>
          <p className="text-gray-600 mt-2">
            Process multiple documents at once with consistent settings
          </p>
        </div>
        {files.length > 0 && (
          <button
            onClick={handleDownloadAll}
            className="btn-secondary flex items-center"
          >
            <Download className="w-5 h-5 mr-2" />
            Download All
          </button>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Upload Files</h2>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="text-gray-600 mb-1">
                {isDragActive
                  ? 'Drop the files here...'
                  : 'Drag & drop files here, or click to select'}
              </p>
              <p className="text-sm text-gray-500">
                Supports multiple TXT, DOCX, PDF files (max 10MB each)
              </p>
            </div>
          </div>

          {files.length > 0 && (
            <div className="card">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">File Queue</h2>
                <button
                  onClick={handleProcessBatch}
                  disabled={processing}
                  className="btn-primary flex items-center disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Process All
                    </>
                  )}
                </button>
              </div>

              <div className="space-y-3">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(file.status)}
                      <div>
                        <p className="font-medium text-sm">{file.name}</p>
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        file.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : file.status === 'processing'
                          ? 'bg-blue-100 text-blue-700'
                          : file.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {file.status}
                      </span>
                      <button
                        onClick={() => handleRemoveFile(file.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Package className="w-5 h-5 mr-2" />
            Batch Settings
          </h2>

          <div className="space-y-4">
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
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-gray-600">
                All files in the queue will be processed with these settings
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BatchProcessing