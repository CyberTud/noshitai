import React from 'react'
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Home,
  FileText,
  User,
  Settings,
  LogOut,
  CreditCard,
  Layers,
  Package
} from 'lucide-react'

const Layout = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center">
                <span className="text-2xl font-bold text-primary-600">NoShitAI</span>
              </Link>

              {isAuthenticated && (
                <div className="ml-10 flex items-center space-x-4">
                  <Link
                    to="/dashboard"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                  >
                    <Home className="w-4 h-4 mr-1" />
                    Dashboard
                  </Link>
                  <Link
                    to="/editor"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    Editor
                  </Link>
                  <Link
                    to="/style-profiles"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                  >
                    <Layers className="w-4 h-4 mr-1" />
                    Style Profiles
                  </Link>
                  <Link
                    to="/batch"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium flex items-center"
                  >
                    <Package className="w-4 h-4 mr-1" />
                    Batch
                  </Link>
                </div>
              )}
            </div>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-700">{user?.email}</span>
                    {!user?.is_premium && (
                      <span className="bg-gray-200 text-gray-700 px-2 py-1 rounded-full text-xs">
                        {user?.credits} credits
                      </span>
                    )}
                    {user?.is_premium && (
                      <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-xs">
                        Premium
                      </span>
                    )}
                  </div>
                  <Link
                    to="/billing"
                    className="text-gray-700 hover:text-primary-600"
                  >
                    <CreditCard className="w-5 h-5" />
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="text-gray-700 hover:text-primary-600"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      <footer className="bg-white mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-600">
            © 2024 NoShitAI. Transform AI text into natural human prose.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout