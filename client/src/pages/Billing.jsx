import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import toast from 'react-hot-toast'
import {
  CreditCard,
  Check,
  X,
  TrendingUp,
  Calendar,
  DollarSign
} from 'lucide-react'

const Billing = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [billingHistory, setBillingHistory] = useState([])

  useEffect(() => {
    fetchBillingHistory()
  }, [])

  const fetchBillingHistory = async () => {
    try {
      const response = await axios.get('/api/billing/history')
      setBillingHistory(response.data)
    } catch (error) {
      console.error('Failed to fetch billing history:', error)
    }
  }

  const handleUpgrade = async () => {
    setLoading(true)
    try {
      const response = await axios.post('/api/billing/subscribe')
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url
      }
    } catch (error) {
      toast.error('Failed to create checkout session')
    }
    setLoading(false)
  }

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return

    try {
      await axios.post('/api/billing/cancel')
      toast.success('Subscription cancelled successfully')
      window.location.reload()
    } catch (error) {
      toast.error('Failed to cancel subscription')
    }
  }

  const plans = [
    {
      name: 'Free',
      price: 0,
      features: [
        '10 credits per month',
        'Basic humanization',
        'Standard processing',
        'Text input only',
        'Basic metrics'
      ],
      notIncluded: [
        'File uploads',
        'Style profiles',
        'Batch processing',
        'API access',
        'Priority support'
      ]
    },
    {
      name: 'Premium',
      price: 29,
      features: [
        'Unlimited processing',
        'All tone styles',
        'Priority processing',
        'File uploads (TXT/DOCX/PDF)',
        'Style profiles',
        'Batch processing',
        'Advanced metrics',
        'API access',
        'Priority support'
      ],
      notIncluded: []
    }
  ]

  const currentPlan = user?.is_premium ? plans[1] : plans[0]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
        <p className="text-gray-600 mt-2">
          Manage your subscription and billing information
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Current Plan</h2>
            <div className="bg-primary-50 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold text-primary-900">
                    {currentPlan.name}
                  </h3>
                  <p className="text-3xl font-bold text-primary-900 mt-2">
                    ${currentPlan.price}
                    <span className="text-lg font-normal text-primary-700">/month</span>
                  </p>
                </div>
                {user?.is_premium ? (
                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">
                    Active
                  </span>
                ) : (
                  <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                    Current
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-medium text-gray-700">Included Features:</h4>
              {currentPlan.features.map((feature, index) => (
                <div key={index} className="flex items-start">
                  <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                  <span className="text-gray-700">{feature}</span>
                </div>
              ))}

              {currentPlan.notIncluded.length > 0 && (
                <>
                  <h4 className="font-medium text-gray-700 mt-4">Not Included:</h4>
                  {currentPlan.notIncluded.map((feature, index) => (
                    <div key={index} className="flex items-start">
                      <X className="w-5 h-5 text-gray-400 mr-2 mt-0.5" />
                      <span className="text-gray-500">{feature}</span>
                    </div>
                  ))}
                </>
              )}
            </div>

            {!user?.is_premium ? (
              <button
                onClick={handleUpgrade}
                disabled={loading}
                className="w-full btn-primary mt-6 py-3 text-lg disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Upgrade to Premium'}
              </button>
            ) : (
              <button
                onClick={handleCancelSubscription}
                className="w-full bg-red-600 text-white px-4 py-3 rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium mt-6"
              >
                Cancel Subscription
              </button>
            )}
          </div>

          {billingHistory.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-4">Billing History</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 text-sm font-medium text-gray-700">Date</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-700">Description</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-700">Amount</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingHistory.map((item, index) => (
                      <tr key={index} className="border-b">
                        <td className="py-3 text-sm">
                          {new Date(item.date).toLocaleDateString()}
                        </td>
                        <td className="py-3 text-sm">{item.description}</td>
                        <td className="py-3 text-sm">${item.amount}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            item.status === 'paid'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-100 text-gray-700'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Usage This Month</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-gray-600">Credits Used</span>
                  <span className="text-sm font-medium">
                    {user?.is_premium ? 'Unlimited' : `${10 - (user?.credits || 0)} / 10`}
                  </span>
                </div>
                {!user?.is_premium && (
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${((10 - (user?.credits || 0)) / 10) * 100}%` }}
                    />
                  </div>
                )}
              </div>

              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600 mb-2">
                  {user?.is_premium
                    ? 'You have unlimited processing with Premium'
                    : `${user?.credits || 0} credits remaining this month`}
                </p>
                {!user?.is_premium && user?.credits === 0 && (
                  <p className="text-sm text-red-600">
                    You've used all your free credits. Upgrade to Premium for unlimited processing.
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Need Help?</h3>
            <p className="text-sm text-gray-600 mb-4">
              Contact our support team for billing inquiries or technical assistance.
            </p>
            <a
              href="mailto:support@noshitai.com"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              support@noshitai.com
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Billing