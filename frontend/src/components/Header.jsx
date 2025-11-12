/**
 * Header component for the application
 * Modern professional design with HiBid branding
 */
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-white shadow-hibid border-b border-hibid-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <Link 
            to="/" 
            className="flex items-center space-x-3 group transition-opacity hover:opacity-80"
          >
            <div className="w-8 h-8 bg-gradient-hibid rounded-lg flex items-center justify-center shadow-hibid">
              <span className="text-white font-bold text-lg">H</span>
            </div>
            <h1 className="text-xl font-bold text-hibid-gray-900 tracking-tight">
              HiBid <span className="text-hibid-blue-600">Email</span>
            </h1>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive('/') || isActive('/campaigns')
                  ? 'bg-hibid-blue-50 text-hibid-blue-700 font-semibold'
                  : 'text-hibid-gray-600 hover:text-hibid-gray-900 hover:bg-hibid-gray-50'
              }`}
            >
              Campaigns
            </Link>
            <Link
              to="/history"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive('/history')
                  ? 'bg-hibid-blue-50 text-hibid-blue-700 font-semibold'
                  : 'text-hibid-gray-600 hover:text-hibid-gray-900 hover:bg-hibid-gray-50'
              }`}
            >
              History
            </Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <Link
              to="/create"
              className="px-4 py-2 bg-gradient-hibid text-white rounded-lg text-sm font-semibold shadow-hibid hover:shadow-hibid-lg transition-all duration-200 hover:scale-105 active:scale-95 flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span className="hidden sm:inline">Create Campaign</span>
              <span className="sm:hidden">Create</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;

