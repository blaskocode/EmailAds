/**
 * ApprovalButtons component - Approve/Reject buttons for campaign
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { approveCampaign } from '../services/api';
import Loading from './Loading';

function ApprovalButtons({ campaignId, onApprovalSuccess }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleApprove = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await approveCampaign(campaignId, 'approve');
      
      // Navigate to success page
      if (onApprovalSuccess) {
        onApprovalSuccess(response);
      } else {
        navigate(`/success/${campaignId}`, { state: { approvalData: response } });
      }
    } catch (err) {
      console.error('Error approving campaign:', err);
      setError(err.response?.data?.detail || 'Failed to approve campaign');
      setShowConfirm(false);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await approveCampaign(campaignId, 'reject');
      
      // Return to upload page
      navigate('/', { 
        state: { 
          message: 'Campaign rejected. You can edit and resubmit.',
          campaignId 
        } 
      });
    } catch (err) {
      console.error('Error rejecting campaign:', err);
      setError(err.response?.data?.detail || 'Failed to reject campaign');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loading message="Processing..." size="sm" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {showConfirm ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
          <p className="text-blue-900 font-medium">
            Are you sure you want to approve this campaign?
          </p>
          <p className="text-blue-700 text-sm">
            This will generate the final HTML file and mark the campaign as approved.
          </p>
          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Yes, Approve
            </button>
            <button
              onClick={() => setShowConfirm(false)}
              disabled={loading}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex gap-4">
          <button
            onClick={handleApprove}
            disabled={loading}
            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            Approve Campaign
          </button>
          <button
            onClick={handleReject}
            disabled={loading}
            className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

export default ApprovalButtons;

