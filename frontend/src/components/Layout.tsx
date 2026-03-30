import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            {/* Logo */}
            <div className="flex items-center gap-8">
              <span className="text-xl font-bold text-indigo-600">
                FinSight
              </span>
              <div className="flex gap-4">
                <Link
                  to="/dashboard"
                  className={`text-sm font-medium px-3 py-2 rounded-md transition-colors ${
                    location.pathname === '/dashboard'
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Portfolio
                </Link>
                <Link
                  to="/chat"
                  className={`text-sm font-medium px-3 py-2 rounded-md transition-colors ${
                    location.pathname === '/chat'
                      ? 'bg-indigo-50 text-indigo-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Agente IA
                </Link>
              </div>
            </div>

            {/* User menu */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Contenido */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}