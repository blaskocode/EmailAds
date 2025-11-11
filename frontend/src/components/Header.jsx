/**
 * Header component for the application
 */
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-gray-900">
              HiBid Email MVP
            </h1>
          </Link>
          <nav className="flex items-center space-x-4">
            <Link
              to="/"
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              New Campaign
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;

