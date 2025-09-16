import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Link } from 'react-router-dom'
import axios from '../services/axios'
import {
  FileText,
  TrendingUp,
  Clock,
  CreditCard,
  Activity,
  Award
} from 'lucide-react'

const Dashboard = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    totalProcessed: 0,
    creditsUsed: 0,
    avgProcessingTime: 0,
    successRate: 100
  })
  const [recentJobs, setRecentJobs] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/user/dashboard')
      setStats(response.data.stats || stats)
      setRecentJobs(response.data.recent_jobs || [])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Welcome back, {user?.full_name || user?.email}!</h1>
        <p className="text-gray-600 mt-2">
          Here's an overview of your NoShitAI usage and activity.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <FileText className="w-8 h-8 text-primary-600" />
            <span className="text-2xl font-bold">{stats.totalProcessed}</span>
          </div>
          <h3 className="text-sm font-medium text-gray-600">Texts Processed</h3>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <CreditCard className="w-8 h-8 text-green-600" />
            <span className="text-2xl font-bold">
              {user?.is_premium ? '∞' : user?.credits || 0}
            </span>
          </div>
          <h3 className="text-sm font-medium text-gray-600">Credits Remaining</h3>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <Clock className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold">{stats.avgProcessingTime}s</span>
          </div>
          <h3 className="text-sm font-medium text-gray-600">Avg Processing Time</h3>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <Activity className="w-8 h-8 text-purple-600" />
            <span className="text-2xl font-bold">{stats.successRate}%</span>
          </div>
          <h3 className="text-sm font-medium text-gray-600">Success Rate</h3>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/editor"
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center">
                <FileText className="w-5 h-5 text-primary-600 mr-3" />
                <div>
                  <p className="font-medium">New Humanization</p>
                  <p className="text-sm text-gray-600">Transform AI text to human-like prose</p>
                </div>
              </div>
              <span className="text-gray-400">→</span>
            </Link>

            <Link
              to="/style-profiles"
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center">
                <Award className="w-5 h-5 text-primary-600 mr-3" />
                <div>
                  <p className="font-medium">Style Profiles</p>
                  <p className="text-sm text-gray-600">Create and manage writing styles</p>
                </div>
              </div>
              <span className="text-gray-400">→</span>
            </Link>

            {!user?.is_premium && (
              <Link
                to="/billing"
                className="flex items-center justify-between p-3 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
              >
                <div className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-primary-600 mr-3" />
                  <div>
                    <p className="font-medium text-primary-900">Upgrade to Premium</p>
                    <p className="text-sm text-primary-700">Unlimited processing & advanced features</p>
                  </div>
                </div>
                <span className="text-primary-600">→</span>
              </Link>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
          {recentJobs.length > 0 ? (
            <div className="space-y-3">
              {recentJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">
                      {job.input_text?.substring(0, 50)}...
                    </p>
                    <p className="text-xs text-gray-600">
                      {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    job.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : job.status === 'processing'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {job.status}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No recent activity. Start by humanizing some text!
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard