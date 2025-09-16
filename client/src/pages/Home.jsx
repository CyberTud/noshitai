import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import {
  Sparkles,
  Shield,
  Zap,
  Target,
  BarChart,
  Users,
  Check
} from 'lucide-react'

const Home = () => {
  const { isAuthenticated } = useAuth()
  const features = [
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: 'Natural Language Transformation',
      description: 'Advanced AI that transforms text into natural, human-like prose while preserving meaning'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Academic Integrity Mode',
      description: 'Built-in safeguards for ethical use with citation preservation and watermarking'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Real-Time Processing',
      description: 'Instant humanization with adjustable parameters and live preview'
    },
    {
      icon: <Target className="w-6 h-6" />,
      title: 'Style Profiles',
      description: 'Create and apply custom writing styles based on sample texts'
    },
    {
      icon: <BarChart className="w-6 h-6" />,
      title: 'Detailed Metrics',
      description: 'Track perplexity, burstiness, readability scores, and more'
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: 'Batch Processing',
      description: 'Process multiple documents efficiently with queue management'
    }
  ]

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      features: [
        '10 credits per month',
        'Basic humanization',
        'Standard processing speed',
        'Text input only',
        'Basic metrics'
      ]
    },
    {
      name: 'Premium',
      price: '$29',
      period: 'per month',
      popular: true,
      features: [
        'Unlimited processing',
        'All tone styles',
        'Priority processing',
        'File uploads (TXT/DOCX/PDF)',
        'Style profiles',
        'Batch processing',
        'Advanced metrics',
        'API access'
      ]
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: 'contact us',
      features: [
        'Everything in Premium',
        'Custom models',
        'Dedicated support',
        'SLA guarantee',
        'On-premise option',
        'Custom integrations'
      ]
    }
  ]

  return (
    <div className="space-y-16">
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6 pt-12"
      >
        <h1 className="text-5xl font-bold text-gray-900">
          Transform AI Text into
          <span className="text-primary-600"> Natural Human Prose</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          NoShitAI uses advanced language processing to humanize AI-generated content
          while preserving citations, maintaining academic integrity, and offering
          transparent controls over writing style.
        </p>
        <div className="flex justify-center space-x-4">
          <Link to={isAuthenticated ? "/editor" : "/register"} className="btn-primary px-8 py-3 text-lg">
            {isAuthenticated ? "Go to Editor" : "Get Started Free"}
          </Link>
          <Link
            to={isAuthenticated ? "/dashboard" : "/editor"}
            className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-300 transition-colors duration-200 font-medium text-lg"
          >
            {isAuthenticated ? "View Dashboard" : "Try Demo"}
          </Link>
        </div>
      </motion.section>

      <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="card hover:shadow-lg transition-shadow"
          >
            <div className="text-primary-600 mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </motion.div>
        ))}
      </section>

      <section className="bg-white rounded-lg shadow-xl p-8">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 text-primary-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              1
            </div>
            <h3 className="font-semibold mb-2">Input Text</h3>
            <p className="text-sm text-gray-600">
              Paste your AI-generated text or upload a document
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 text-primary-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              2
            </div>
            <h3 className="font-semibold mb-2">Adjust Settings</h3>
            <p className="text-sm text-gray-600">
              Choose tone, formality, and other parameters
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 text-primary-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              3
            </div>
            <h3 className="font-semibold mb-2">Process</h3>
            <p className="text-sm text-gray-600">
              Our engine humanizes your text in seconds
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 text-primary-600 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              4
            </div>
            <h3 className="font-semibold mb-2">Download</h3>
            <p className="text-sm text-gray-600">
              Export your humanized text with metrics report
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold text-center mb-8">Choose Your Plan</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`card ${
                plan.popular ? 'ring-2 ring-primary-500 relative' : ''
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary-500 text-white px-3 py-1 rounded-full text-sm">
                  Most Popular
                </span>
              )}
              <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
              <div className="mb-4">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-gray-600 ml-2">/{plan.period}</span>
              </div>
              <ul className="space-y-2 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-start">
                    <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              <Link
                to={isAuthenticated ? (plan.name === 'Free' ? "/editor" : "/billing") : "/register"}
                className={`block text-center py-2 px-4 rounded-lg font-medium ${
                  plan.popular
                    ? 'bg-primary-600 text-white hover:bg-primary-700'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                } transition-colors`}
              >
                {isAuthenticated
                  ? (plan.name === 'Free' ? 'Go to Editor' : plan.name === 'Enterprise' ? 'Contact Us' : 'Upgrade Now')
                  : 'Get Started'}
              </Link>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home