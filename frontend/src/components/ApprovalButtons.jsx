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
  const [showRejectConfirm, setShowRejectConfirm] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);

  const handleApprove = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await approveCampaign(campaignId, 'approve', feedback.trim() || null);
      
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
    if (!showRejectConfirm) {
      setShowRejectConfirm(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      await approveCampaign(campaignId, 'reject', feedback.trim() || null);
      
      // Navigate to campaigns list page
      navigate('/campaigns');
    } catch (err) {
      console.error('Error rejecting campaign:', err);
      setError(err.response?.data?.detail || 'Failed to reject campaign');
      setShowRejectConfirm(false);
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
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl shadow-hibid">
          {error}
        </div>
      )}

      {/* Feedback Section */}
      {showFeedback && (
        <div className="bg-hibid-gray-50 border border-hibid-gray-200 rounded-xl p-4 space-y-3 shadow-hibid">
          <label className="block text-sm font-medium text-hibid-gray-700">
            Feedback or Comments (Optional)
          </label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Add any feedback, comments, or notes about this campaign..."
            className="w-full px-3 py-2 border border-hibid-gray-300 rounded-lg focus:ring-2 focus:ring-hibid-blue-500 focus:border-hibid-blue-500 resize-none transition-colors"
            rows={4}
            maxLength={2000}
          />
          <p className="text-xs text-hibid-gray-500">
            {feedback.length}/2000 characters
          </p>
          <button
            onClick={() => setShowFeedback(false)}
            className="text-sm text-hibid-gray-600 hover:text-hibid-gray-800 transition-colors"
          >
            Hide feedback
          </button>
        </div>
      )}

      {showConfirm ? (
        <div className="bg-hibid-blue-50 border border-hibid-blue-200 rounded-xl p-4 space-y-4 shadow-hibid">
          <p className="text-hibid-blue-900 font-semibold">
            Are you sure you want to approve this campaign?
          </p>
          <p className="text-hibid-blue-700 text-sm">
            This will generate the final HTML file and mark the campaign as approved.
          </p>
          {feedback && (
            <div className="bg-white rounded-lg p-3 border border-hibid-blue-200">
              <p className="text-xs font-medium text-hibid-gray-700 mb-1">Your feedback:</p>
              <p className="text-sm text-hibid-gray-600">{feedback}</p>
            </div>
          )}
          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-4 py-2.5 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid hover:shadow-hibid-lg"
            >
              Yes, Approve
            </button>
            <button
              onClick={() => setShowConfirm(false)}
              disabled={loading}
              className="flex-1 bg-hibid-gray-200 text-hibid-gray-700 px-4 py-2.5 rounded-lg font-medium hover:bg-hibid-gray-300 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : showRejectConfirm ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 space-y-4 shadow-hibid">
          <p className="text-red-900 font-semibold">
            Are you sure you want to reject this campaign?
          </p>
          <p className="text-red-700 text-sm">
            This will mark the campaign as rejected. You can view and edit it from the campaigns list.
          </p>
          {feedback && (
            <div className="bg-white rounded-lg p-3 border border-red-200">
              <p className="text-xs font-medium text-hibid-gray-700 mb-1">Your feedback:</p>
              <p className="text-sm text-hibid-gray-600">{feedback}</p>
            </div>
          )}
          <div className="flex gap-3">
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex-1 bg-red-600 text-white px-4 py-2.5 rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid hover:shadow-hibid-lg"
            >
              Yes, Reject
            </button>
            <button
              onClick={() => setShowRejectConfirm(false)}
              disabled={loading}
              className="flex-1 bg-hibid-gray-200 text-hibid-gray-700 px-4 py-2.5 rounded-lg font-medium hover:bg-hibid-gray-300 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex gap-4">
            <button
              onClick={handleApprove}
              disabled={loading}
              className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid hover:shadow-hibid-lg"
            >
              Approve Campaign
            </button>
            <button
              onClick={handleReject}
              disabled={loading}
              className="flex-1 bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid hover:shadow-hibid-lg"
            >
              Reject
            </button>
          </div>
          <button
            onClick={() => setShowFeedback(!showFeedback)}
            className="w-full text-sm text-hibid-gray-600 hover:text-hibid-gray-800 underline transition-colors"
          >
            {showFeedback ? 'Hide' : 'Add'} feedback or comments
          </button>
        </div>
      )}
    </div>
  );
}

export default ApprovalButtons;

