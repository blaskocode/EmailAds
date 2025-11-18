/**
 * Campaigns List Page - View and manage all campaigns
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import ScheduleModal from '../components/ScheduleModal';
import StatsCards from '../components/StatsCards';
import CampaignsSearchBar from '../components/CampaignsSearchBar';
import StatusBadge from '../components/StatusBadge';
import { listCampaigns, resetCampaign, scheduleCampaign, cancelSchedule } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import {
  STATUS_OPTIONS,
  STATUS_COLORS,
  REVIEW_STATUS_COLORS,
  formatDate,
  truncateText,
  getTimeUntilScheduled
} from '../utils/campaignsListUtils';

function CampaignsListPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [total, setTotal] = useState(0);
  const [limit] = useState(100);
  const [offset, setOffset] = useState(0);
  const [resettingId, setResettingId] = useState(null);
  const [schedulingId, setSchedulingId] = useState(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [scheduleDateTime, setScheduleDateTime] = useState('');
  const [cancelingId, setCancelingId] = useState(null);
  const [stats, setStats] = useState({ total: 0, approved: 0, rejected: 0, ready: 0 });

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
      
      const response = await listCampaigns({ ...params, include_stats: true });
      setCampaigns(response.campaigns || []);
      setTotal(response.total || 0);
      
      // Calculate stats from response or campaigns
      if (response.stats) {
        setStats(response.stats);
      } else {
        const campaignStats = {
          total: response.total || 0,
          approved: (response.campaigns || []).filter(c => c.status === 'approved').length,
          rejected: (response.campaigns || []).filter(c => c.status === 'rejected').length,
          ready: (response.campaigns || []).filter(c => c.status === 'ready' || c.status === 'processed').length,
        };
        setStats(campaignStats);
      }
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

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setOffset(0); // Reset to first page when search changes
  };

  // Filter campaigns by search query
  const filteredCampaigns = campaigns.filter(campaign => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      (campaign.campaign_name || '').toLowerCase().includes(query) ||
      (campaign.advertiser_name || '').toLowerCase().includes(query) ||
      (campaign.id || '').toLowerCase().includes(query) ||
      (campaign.feedback || '').toLowerCase().includes(query)
    );
  });

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


  const handleScheduleClick = (campaign, e) => {
    e.stopPropagation();
    setSelectedCampaign(campaign);
    // Set default to 1 hour from now
    const defaultDate = new Date();
    defaultDate.setHours(defaultDate.getHours() + 1);
    setScheduleDateTime(defaultDate.toISOString().slice(0, 16)); // Format: YYYY-MM-DDTHH:mm
    setShowScheduleModal(true);
  };

  const handleScheduleSubmit = async () => {
    if (!selectedCampaign || !scheduleDateTime) return;
    
    try {
      setSchedulingId(selectedCampaign.id);
      // Convert local datetime to ISO 8601 format
      const scheduledAt = new Date(scheduleDateTime).toISOString();
      await scheduleCampaign(selectedCampaign.id, scheduledAt);
      showToast('Campaign scheduled successfully', 'success');
      setShowScheduleModal(false);
      setSelectedCampaign(null);
      setScheduleDateTime('');
      await loadCampaigns();
    } catch (err) {
      console.error('Error scheduling campaign:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to schedule campaign';
      showToast(errorMessage, 'error');
    } finally {
      setSchedulingId(null);
    }
  };

  const handleCancelSchedule = async (campaignId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('Cancel this scheduled campaign?')) {
      return;
    }

    try {
      setCancelingId(campaignId);
      await cancelSchedule(campaignId);
      showToast('Schedule canceled successfully', 'success');
      await loadCampaigns();
    } catch (err) {
      console.error('Error canceling schedule:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to cancel schedule';
      showToast(errorMessage, 'error');
    } finally {
      setCancelingId(null);
    }
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
    <div className="container mx-auto px-4 py-6 lg:px-6 max-w-7xl">
      {/* Dashboard Stats Cards */}
      <StatsCards stats={stats} />

      {/* Header with Search and Filters */}
      <CampaignsSearchBar
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        statusFilter={statusFilter}
        onStatusFilterChange={handleStatusFilterChange}
      />

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
      {filteredCampaigns.length > 0 ? (
        <div className="bg-white rounded-xl shadow-hibid overflow-hidden border border-hibid-gray-200">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-hibid-gray-200">
              <thead className="bg-hibid-gray-50">
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
                    Scheduled
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Feedback
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-hibid-gray-200">
                {filteredCampaigns.map((campaign) => (
                  <tr
                    key={campaign.id}
                    onClick={() => handleViewCampaign(campaign.id, campaign.status, null)}
                    className="hover:bg-hibid-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-hibid-gray-900">
                        {campaign.campaign_name || 'Untitled Campaign'}
                      </div>
                      <div className="text-xs text-hibid-gray-500 mt-1">
                        ID: {campaign.id.substring(0, 8)}...
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-hibid-gray-900">
                        {campaign.advertiser_name || '—'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col gap-1.5">
                        <StatusBadge status={campaign.status} />
                        {campaign.scheduling_status === 'scheduled' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg border bg-purple-50 text-purple-700 border-purple-200 shadow-sm">
                            <svg className="w-3.5 h-3.5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Scheduled
                          </span>
                        )}
                        {campaign.review_status && (
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-lg border shadow-sm ${
                            campaign.review_status === 'pending' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                            campaign.review_status === 'reviewed' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                            campaign.review_status === 'approved' ? 'bg-green-50 text-green-700 border-green-200' :
                            'bg-red-50 text-red-700 border-red-200'
                          }`}>
                            <svg className={`w-3.5 h-3.5 ${
                              campaign.review_status === 'pending' ? 'text-yellow-500' :
                              campaign.review_status === 'reviewed' ? 'text-blue-500' :
                              campaign.review_status === 'approved' ? 'text-green-500' :
                              'text-red-500'
                            }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Review: {campaign.review_status}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-hibid-gray-900">
                        {formatDate(campaign.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {campaign.scheduling_status === 'scheduled' && campaign.scheduled_at ? (
                        <div className="text-sm">
                          <div className="text-hibid-gray-900 font-medium">
                            {formatDate(campaign.scheduled_at)}
                          </div>
                          <div className="text-xs text-purple-600 mt-1">
                            {getTimeUntilScheduled(campaign.scheduled_at)}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-hibid-gray-400">—</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-hibid-gray-600 max-w-xs">
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
                        {campaign.status === 'ready' || campaign.status === 'processed' ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/review/${campaign.id}`);
                            }}
                            className="px-3 py-1 text-xs bg-indigo-100 text-indigo-800 rounded hover:bg-indigo-200"
                          >
                            Review
                          </button>
                        ) : null}
                        {campaign.status === 'approved' && campaign.scheduling_status !== 'scheduled' && (
                          <button
                            onClick={(e) => handleScheduleClick(campaign, e)}
                            className="px-3 py-1 text-xs bg-purple-100 text-purple-800 rounded hover:bg-purple-200"
                          >
                            Schedule
                          </button>
                        )}
                        {campaign.scheduling_status === 'scheduled' && (
                          <button
                            onClick={(e) => handleCancelSchedule(campaign.id, e)}
                            disabled={cancelingId === campaign.id}
                            className="px-3 py-1 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {cancelingId === campaign.id ? 'Canceling...' : 'Cancel'}
                          </button>
                        )}
                        <button
                          onClick={(e) => handleViewCampaign(campaign.id, campaign.status, e)}
                          className="px-3 py-1 text-xs bg-hibid-blue-100 text-hibid-blue-800 rounded hover:bg-hibid-blue-200 transition-colors"
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
            <div className="bg-hibid-gray-50 px-6 py-4 border-t border-hibid-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-hibid-gray-700">
                  Showing {offset + 1} to {Math.min(offset + limit, filteredCampaigns.length)} of {filteredCampaigns.length} {searchQuery ? 'filtered' : ''} campaigns
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setOffset(Math.max(0, offset - limit))}
                    disabled={offset === 0}
                    className="px-4 py-2 text-sm border border-hibid-gray-300 rounded-lg hover:bg-hibid-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setOffset(offset + limit)}
                    disabled={offset + limit >= filteredCampaigns.length}
                    className="px-4 py-2 text-sm border border-hibid-gray-300 rounded-lg hover:bg-hibid-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-hibid p-12 border border-hibid-gray-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-hibid-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-hibid-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-hibid-gray-600 text-lg font-medium mb-2">
              {searchQuery 
                ? `No campaigns found matching "${searchQuery}"`
                : statusFilter 
                ? `No campaigns found with status "${statusFilter}"`
                : 'No campaigns found. Create your first campaign to get started!'}
            </p>
            {!statusFilter && !searchQuery && (
              <button
                onClick={() => navigate('/create')}
                className="mt-4 px-6 py-2 bg-gradient-hibid text-white rounded-lg hover:shadow-hibid-lg transition-all duration-200 font-semibold"
              >
                Create Campaign
              </button>
            )}
          </div>
        </div>
      )}

      {/* Schedule Modal */}
      <ScheduleModal
        show={showScheduleModal}
        campaign={selectedCampaign}
        scheduleDateTime={scheduleDateTime}
        onDateTimeChange={setScheduleDateTime}
        onSubmit={handleScheduleSubmit}
        onCancel={() => {
          setShowScheduleModal(false);
          setSelectedCampaign(null);
          setScheduleDateTime('');
        }}
        isScheduling={schedulingId === selectedCampaign?.id}
      />
    </div>
  );
}

export default CampaignsListPage;

