import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Editor from './pages/Editor'
import StyleProfiles from './pages/StyleProfiles'
import BatchProcessing from './pages/BatchProcessing'
import Billing from './pages/Billing'
import PrivateRoute from './components/PrivateRoute'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Toaster position="top-right" />
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Home />} />
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
              <Route path="dashboard" element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              } />
              <Route path="editor" element={
                <PrivateRoute>
                  <Editor />
                </PrivateRoute>
              } />
              <Route path="style-profiles" element={
                <PrivateRoute>
                  <StyleProfiles />
                </PrivateRoute>
              } />
              <Route path="batch" element={
                <PrivateRoute>
                  <BatchProcessing />
                </PrivateRoute>
              } />
              <Route path="billing" element={
                <PrivateRoute>
                  <Billing />
                </PrivateRoute>
              } />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App