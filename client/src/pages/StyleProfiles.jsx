import React, { useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'
import { Plus, Edit, Trash2, FileText, BarChart } from 'lucide-react'

const StyleProfiles = () => {
  const [profiles, setProfiles] = useState([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newProfile, setNewProfile] = useState({
    name: '',
    description: '',
    sample_text: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchProfiles()
  }, [])

  const fetchProfiles = async () => {
    try {
      const response = await axios.get('/api/style-profiles')
      setProfiles(response.data)
    } catch (error) {
      toast.error('Failed to fetch style profiles')
    }
  }

  const handleCreateProfile = async (e) => {
    e.preventDefault()
    if (!newProfile.name || !newProfile.sample_text) {
      toast.error('Please provide a name and sample text')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post('/api/style-profiles', newProfile)
      setProfiles([...profiles, response.data])
      setNewProfile({ name: '', description: '', sample_text: '' })
      setShowCreateModal(false)
      toast.success('Style profile created successfully')
    } catch (error) {
      toast.error('Failed to create style profile')
    }
    setLoading(false)
  }

  const handleDeleteProfile = async (id) => {
    if (!confirm('Are you sure you want to delete this profile?')) return

    try {
      await axios.delete(`/api/style-profiles/${id}`)
      setProfiles(profiles.filter(p => p.id !== id))
      toast.success('Profile deleted successfully')
    } catch (error) {
      toast.error('Failed to delete profile')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Style Profiles</h1>
          <p className="text-gray-600 mt-2">
            Create custom writing styles based on sample texts
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Profile
        </button>
      </div>

      {profiles.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profiles.map((profile) => (
            <div key={profile.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{profile.name}</h3>
                  {profile.description && (
                    <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDeleteProfile(profile.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Sample Text</p>
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {profile.sample_text}
                  </p>
                </div>

                {profile.metrics && (
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-blue-50 p-2 rounded">
                      <p className="text-xs text-blue-600">FK Grade</p>
                      <p className="text-sm font-semibold text-blue-900">
                        {profile.metrics.flesch_kincaid_grade?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-green-50 p-2 rounded">
                      <p className="text-xs text-green-600">Lexical Div</p>
                      <p className="text-sm font-semibold text-green-900">
                        {((profile.metrics.lexical_diversity || 0) * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-gray-500">
                  Created {new Date(profile.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Style Profiles Yet
          </h3>
          <p className="text-gray-600 mb-4">
            Create your first style profile to match specific writing patterns
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary mx-auto"
          >
            Create First Profile
          </button>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Create Style Profile</h2>
            <form onSubmit={handleCreateProfile} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Profile Name
                </label>
                <input
                  type="text"
                  value={newProfile.name}
                  onChange={(e) => setNewProfile({ ...newProfile, name: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Academic Writing, Blog Post Style"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <input
                  type="text"
                  value={newProfile.description}
                  onChange={(e) => setNewProfile({ ...newProfile, description: e.target.value })}
                  className="input-field"
                  placeholder="Brief description of this style"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sample Text
                </label>
                <textarea
                  value={newProfile.sample_text}
                  onChange={(e) => setNewProfile({ ...newProfile, sample_text: e.target.value })}
                  className="w-full h-48 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Paste a sample text that represents this writing style..."
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Provide at least 200 words for better style analysis
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Profile'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default StyleProfiles