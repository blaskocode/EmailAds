/**
 * Campaigns Search Bar Component - Search and filter controls
 */
import { STATUS_OPTIONS } from '../utils/campaignsListUtils';

function CampaignsSearchBar({ searchQuery, onSearchChange, statusFilter, onStatusFilterChange }) {
  return (
    <div className="bg-white rounded-xl shadow-hibid p-6 mb-6 border border-hibid-gray-200">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-4">
        <div>
          <h2 className="text-2xl font-bold text-hibid-gray-900 mb-1">
            Campaigns
          </h2>
          <p className="text-hibid-gray-600 text-sm">
            Manage and track all your email campaigns
          </p>
        </div>
        
        {/* Search Bar */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-hibid-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search campaigns..."
              value={searchQuery}
              onChange={onSearchChange}
              className="block w-full pl-10 pr-3 py-2 border border-hibid-gray-300 rounded-lg focus:ring-2 focus:ring-hibid-blue-500 focus:border-hibid-blue-500 text-sm"
            />
          </div>
        </div>
        
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <label htmlFor="status-filter" className="text-sm font-medium text-hibid-gray-700 whitespace-nowrap">
            Status:
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={onStatusFilterChange}
            className="px-4 py-2 border border-hibid-gray-300 rounded-lg focus:ring-2 focus:ring-hibid-blue-500 focus:border-hibid-blue-500 text-sm bg-white"
          >
            {STATUS_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

export default CampaignsSearchBar;

