import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import MapPage from '@/pages/MapPage'
import AuthPage from '@/pages/AuthPage'
import LandDetailPage from '@/pages/LandDetailPage'
import CabinetPage from '@/pages/CabinetPage'
import ServicesPage from '@/pages/ServicesPage'
import CompaniesPage from '@/pages/CompaniesPage'
import CompanyDetailPage from '@/pages/CompanyDetailPage'
import PlanDetailPage from '@/pages/PlanDetailPage'
import BankruptcyAuctionsPage from '@/pages/BankruptcyAuctionsPage'
import GovernmentSalesPage from '@/pages/GovernmentSalesPage'
import CreateListingPage from '@/pages/CreateListingPage'
import '@/App.css'

function App() {
  const { user, loadUser } = useAuthStore()

  useEffect(() => {
    loadUser()
  }, [])

  const ProtectedRoute = ({ element }: { element: React.ReactElement }) => {
    if (!user) {
      return <Navigate to="/auth" replace />
    }
    return element
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<MapPage />} />
        <Route path="/land/:id" element={<LandDetailPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route path="/company/:id" element={<CompanyDetailPage />} />
        <Route path="/cabinet" element={<ProtectedRoute element={<CabinetPage />} />} />
        <Route path="/plan/:id" element={<ProtectedRoute element={<PlanDetailPage />} />} />
        <Route path="/bankruptcy-auctions" element={<BankruptcyAuctionsPage />} />
        <Route path="/government-sales" element={<GovernmentSalesPage />} />
        <Route path="/create-listing" element={<ProtectedRoute element={<CreateListingPage />} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
