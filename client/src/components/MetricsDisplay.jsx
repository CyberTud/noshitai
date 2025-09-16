import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const MetricsDisplay = ({ metrics }) => {
  if (!metrics) return null

  const formatMetric = (value) => {
    if (typeof value === 'number') {
      return value.toFixed(2)
    }
    return value
  }

  const getChangeIcon = (original, humanized) => {
    const diff = humanized - original
    if (Math.abs(diff) < 0.01) return <Minus className="w-4 h-4 text-gray-500" />
    if (diff > 0) return <TrendingUp className="w-4 h-4 text-green-500" />
    return <TrendingDown className="w-4 h-4 text-red-500" />
  }

  const chartData = [
    {
      name: 'FK Grade',
      Original: metrics.flesch_kincaid_original,
      Humanized: metrics.flesch_kincaid_humanized
    },
    {
      name: 'Burstiness',
      Original: metrics.burstiness_original,
      Humanized: metrics.burstiness_humanized
    },
    {
      name: 'Avg Sentence',
      Original: metrics.avg_sentence_length_original,
      Humanized: metrics.avg_sentence_length_humanized
    },
    {
      name: 'Lexical Div',
      Original: metrics.lexical_diversity_original * 100,
      Humanized: metrics.lexical_diversity_humanized * 100
    }
  ]

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Metrics Analysis</h2>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Flesch-Kincaid Grade</span>
            {getChangeIcon(metrics.flesch_kincaid_original, metrics.flesch_kincaid_humanized)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-semibold">
              {formatMetric(metrics.flesch_kincaid_humanized)}
            </span>
            <span className="text-sm text-gray-500">
              from {formatMetric(metrics.flesch_kincaid_original)}
            </span>
          </div>
        </div>

        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Perplexity</span>
          </div>
          <span className="text-lg font-semibold">
            {formatMetric(metrics.perplexity)}
          </span>
        </div>

        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Burstiness</span>
            {getChangeIcon(metrics.burstiness_original, metrics.burstiness_humanized)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-semibold">
              {formatMetric(metrics.burstiness_humanized)}
            </span>
            <span className="text-sm text-gray-500">
              from {formatMetric(metrics.burstiness_original)}
            </span>
          </div>
        </div>

        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-gray-600">Lexical Diversity</span>
            {getChangeIcon(metrics.lexical_diversity_original, metrics.lexical_diversity_humanized)}
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-semibold">
              {(metrics.lexical_diversity_humanized * 100).toFixed(1)}%
            </span>
            <span className="text-sm text-gray-500">
              from {(metrics.lexical_diversity_original * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Original" fill="#9CA3AF" />
            <Bar dataKey="Humanized" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default MetricsDisplay