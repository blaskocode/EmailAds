/**
 * Stats Cards Component - Dashboard overview statistics
 */
function StatsCards({ stats }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-gradient-hibid rounded-xl shadow-hibid p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-hibid-blue-100 text-sm font-medium mb-1">Total Campaigns</p>
            <p className="text-3xl font-bold">{stats.total}</p>
          </div>
          <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-hibid p-6 border border-hibid-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-hibid-gray-600 text-sm font-medium mb-1">Approved</p>
            <p className="text-3xl font-bold text-hibid-gray-900">{stats.approved}</p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-hibid p-6 border border-hibid-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-hibid-gray-600 text-sm font-medium mb-1">Ready</p>
            <p className="text-3xl font-bold text-hibid-gray-900">{stats.ready}</p>
          </div>
          <div className="w-12 h-12 bg-hibid-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-hibid-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-hibid p-6 border border-hibid-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-hibid-gray-600 text-sm font-medium mb-1">Rejected</p>
            <p className="text-3xl font-bold text-hibid-gray-900">{stats.rejected}</p>
          </div>
          <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsCards;

