/**
 * Campaign History Page - Show last 10 campaigns with quick actions
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import { listCampaigns, downloadCampaign } from '../services/api';
import { useToast } from '../contexts/ToastContext';

const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-800',
  uploaded: 'bg-blue-100 text-blue-800',
  processed: 'bg-yellow-100 text-yellow-800',
  ready: 'bg-green-100 text-green-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800'
};

function HistoryPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingId, setDownloadingId] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get last 10 campaigns with stats
      const response = await listCampaigns({ 
        last_n: 10,
        include_stats: true 
      });
      setCampaigns(response.campaigns || []);
    } catch (err) {
      console.error('Error loading history:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load campaign history';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleViewPreview = (campaignId, status, e) => {
    if (e) {
      e.stopPropagation();
    }
    
    if (status === 'ready' || status === 'processed') {
      navigate(`/preview/${campaignId}`);
    } else if (status === 'approved') {
      navigate(`/success/${campaignId}`);
    } else {
      // For other statuses, navigate to upload page for editing
      navigate(`/`, { state: { editCampaignId: campaignId } });
    }
  };

  const handleDownload = async (campaignId, campaignName, e) => {
    if (e) {
      e.stopPropagation();
    }
    
    try {
      setDownloadingId(campaignId);
      const blob = await downloadCampaign(campaignId);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${campaignName || 'campaign'}_${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      showToast('HTML file downloaded successfully', 'success');
    } catch (err) {
      console.error('Error downloading campaign:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to download campaign';
      showToast(errorMessage, 'error');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleEdit = (campaignId, e) => {
    if (e) {
      e.stopPropagation();
    }
    navigate(`/`, { state: { editCampaignId: campaignId } });
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

  if (loading && campaigns.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading message="Loading campaign history..." />
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
              Campaign History
            </h2>
            <p className="text-gray-600">
              Last 10 campaigns
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/campaigns')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              View All Campaigns
            </button>
            <button
              onClick={() => navigate('/create')}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              New Campaign
            </button>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && campaigns.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-red-600 mb-2">Error Loading History</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={loadHistory}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Campaigns Grid */}
      {campaigns.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              {/* Campaign Header */}
              <div className="mb-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {campaign.campaign_name || 'Untitled Campaign'}
                  </h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ml-2 ${
                    STATUS_COLORS[campaign.status] || STATUS_COLORS.draft
                  }`}>
                    {campaign.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {campaign.advertiser_name || '—'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatDate(campaign.created_at)}
                </p>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap gap-2 mt-4">
                {/* View Preview Button */}
                <button
                  onClick={(e) => handleViewPreview(campaign.id, campaign.status, e)}
                  className="flex-1 px-3 py-2 text-xs font-medium text-blue-700 bg-blue-50 rounded hover:bg-blue-100 transition-colors"
                >
                  {campaign.status === 'ready' || campaign.status === 'processed' 
                    ? 'View Preview' 
                    : campaign.status === 'approved'
                    ? 'View'
                    : 'Edit'}
                </button>

                {/* Download Button (for approved campaigns) */}
                {campaign.status === 'approved' && (
                  <button
                    onClick={(e) => handleDownload(campaign.id, campaign.campaign_name, e)}
                    disabled={downloadingId === campaign.id}
                    className="flex-1 px-3 py-2 text-xs font-medium text-emerald-700 bg-emerald-50 rounded hover:bg-emerald-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {downloadingId === campaign.id ? 'Downloading...' : 'Re-download'}
                  </button>
                )}

                {/* Edit Button (for rejected campaigns) */}
                {campaign.status === 'rejected' && (
                  <button
                    onClick={(e) => handleEdit(campaign.id, e)}
                    className="flex-1 px-3 py-2 text-xs font-medium text-yellow-700 bg-yellow-50 rounded hover:bg-yellow-100 transition-colors"
                  >
                    Edit
                  </button>
                )}
              </div>

              {/* Campaign ID (small) */}
              <p className="text-xs text-gray-400 mt-3 pt-3 border-t border-gray-100">
                ID: {campaign.id.substring(0, 8)}...
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <p className="text-gray-600 text-lg">
              No campaign history found. Create your first campaign to get started!
            </p>
            <button
              onClick={() => navigate('/create')}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Campaign
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default HistoryPage;

