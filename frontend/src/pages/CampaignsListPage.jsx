/**
 * Campaigns List Page - View and manage all campaigns
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import { listCampaigns, resetCampaign } from '../services/api';
import { useToast } from '../contexts/ToastContext';

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'uploaded', label: 'Uploaded' },
  { value: 'processed', label: 'Processed' },
  { value: 'ready', label: 'Ready' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' }
];

const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-800',
  uploaded: 'bg-blue-100 text-blue-800',
  processed: 'bg-yellow-100 text-yellow-800',
  ready: 'bg-green-100 text-green-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800'
};

function CampaignsListPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [total, setTotal] = useState(0);
  const [limit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [resettingId, setResettingId] = useState(null);

  useEffect(() => {
    loadCampaigns();
  }, [statusFilter, offset]);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        limit,
        offset
      };
      
      if (statusFilter) {
        params.status = statusFilter;
      }
      
      const response = await listCampaigns(params);
      setCampaigns(response.campaigns || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Error loading campaigns:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load campaigns';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
    setOffset(0); // Reset to first page when filter changes
  };

  const handleViewCampaign = (campaignId, status, e) => {
    if (e) {
      e.stopPropagation(); // Prevent row click if called from button
    }
    
    if (status === 'ready' || status === 'processed') {
      navigate(`/preview/${campaignId}`);
    } else if (status === 'approved') {
      navigate(`/success/${campaignId}`);
    } else {
      // For other statuses (including rejected), navigate to upload page for editing
      navigate(`/`, { state: { editCampaignId: campaignId } });
    }
  };

  const handleResetCampaign = async (campaignId, e) => {
    e.stopPropagation(); // Prevent row click
    
    if (!window.confirm('Reset this rejected campaign to uploaded status? This will allow you to resubmit it.')) {
      return;
    }

    try {
      setResettingId(campaignId);
      await resetCampaign(campaignId, false);
      showToast('Campaign reset successfully. You can now edit and resubmit it.', 'success');
      await loadCampaigns(); // Reload list
    } catch (err) {
      console.error('Error resetting campaign:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to reset campaign';
      showToast(errorMessage, 'error');
    } finally {
      setResettingId(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const truncateText = (text, maxLength = 50) => {
    if (!text) return '—';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (loading && campaigns.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading message="Loading campaigns..." />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              All Campaigns
            </h2>
            <p className="text-gray-600">
              {total} {total === 1 ? 'campaign' : 'campaigns'} total
            </p>
          </div>
          
          {/* Status Filter */}
          <div className="flex items-center gap-4">
            <label htmlFor="status-filter" className="text-sm font-medium text-gray-700">
              Filter by Status:
            </label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={handleStatusFilterChange}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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

      {/* Error State */}
      {error && campaigns.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-red-600 mb-2">Error Loading Campaigns</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={loadCampaigns}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Campaigns Table */}
      {campaigns.length > 0 ? (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Advertiser
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feedback
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {campaigns.map((campaign) => (
                  <tr
                    key={campaign.id}
                    onClick={() => handleViewCampaign(campaign.id, campaign.status, null)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {campaign.campaign_name || 'Untitled Campaign'}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        ID: {campaign.id.substring(0, 8)}...
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {campaign.advertiser_name || '—'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        STATUS_COLORS[campaign.status] || STATUS_COLORS.draft
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(campaign.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-600 max-w-xs">
                        {truncateText(campaign.feedback, 60)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        {campaign.status === 'rejected' && (
                          <button
                            onClick={(e) => handleResetCampaign(campaign.id, e)}
                            disabled={resettingId === campaign.id}
                            className="px-3 py-1 text-xs bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {resettingId === campaign.id ? 'Resetting...' : 'Reset'}
                          </button>
                        )}
                        <button
                          onClick={(e) => handleViewCampaign(campaign.id, campaign.status, e)}
                          className="px-3 py-1 text-xs bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                        >
                          {campaign.status === 'ready' || campaign.status === 'processed' 
                            ? 'Preview' 
                            : campaign.status === 'approved'
                            ? 'View'
                            : 'Edit'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Pagination */}
          {total > limit && (
            <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {offset + 1} to {Math.min(offset + limit, total)} of {total} campaigns
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setOffset(Math.max(0, offset - limit))}
                    disabled={offset === 0}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setOffset(offset + limit)}
                    disabled={offset + limit >= total}
                    className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <p className="text-gray-600 text-lg">
              {statusFilter 
                ? `No campaigns found with status "${statusFilter}"`
                : 'No campaigns found. Create your first campaign to get started!'}
            </p>
            {!statusFilter && (
              <button
                onClick={() => navigate('/')}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Campaign
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default CampaignsListPage;

