/**
 * Review Page - Editorial review interface for campaign managers
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import PreviewFrame from '../components/PreviewFrame';
import CampaignDetails from '../components/CampaignDetails';
import { getCampaignDetail, reviewCampaign, editCampaignContent, getPreview } from '../services/api';
import { useToast } from '../contexts/ToastContext';

const REVIEW_STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending Review', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'reviewed', label: 'Reviewed', color: 'bg-blue-100 text-blue-800' },
  { value: 'approved', label: 'Approved', color: 'bg-green-100 text-green-800' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' }
];

function ReviewPage() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviewStatus, setReviewStatus] = useState('pending');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(null);
  const [previewHtml, setPreviewHtml] = useState(null);

  useEffect(() => {
    if (campaignId) {
      loadCampaign();
      loadPreview();
    }
  }, [campaignId]);

  const loadCampaign = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await getCampaignDetail(campaignId);
      setCampaign(data);
      
      // Pre-fill review status and notes if they exist
      if (data.review_status) {
        setReviewStatus(data.review_status);
      }
      if (data.reviewer_notes) {
        setReviewerNotes(data.reviewer_notes);
      }
      
      // Initialize edited content from campaign data
      if (data.ai_processing_data?.content) {
        setEditedContent({ ...data.ai_processing_data.content });
      }
    } catch (err) {
      console.error('Error loading campaign:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load campaign';
      setError(errorMessage);
      showToast(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async () => {
    try {
      const previewData = await getPreview(campaignId);
      if (previewData?.html_preview) {
        setPreviewHtml(previewData.html_preview);
      }
    } catch (err) {
      console.error('Error loading preview:', err);
      // Preview loading failure is not critical, just log it
    }
  };

  const handleReviewSubmit = async () => {
    if (!campaign) return;
    
    try {
      setIsSubmitting(true);
      
      // If content was edited, save edits first
      if (isEditing && editedContent) {
        await editCampaignContent(campaign.id, editedContent);
        showToast('Content edits saved', 'success');
      }
      
      // Submit review
      await reviewCampaign(campaign.id, reviewStatus, reviewerNotes);
      showToast('Review submitted successfully', 'success');
      
      // Reload campaign to get updated data
      await loadCampaign();
      setIsEditing(false);
    } catch (err) {
      console.error('Error submitting review:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to submit review';
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleContentEdit = (field, value) => {
    if (!editedContent) return;
    setEditedContent({
      ...editedContent,
      [field]: value
    });
  };

  const handleMarkAsReviewed = async () => {
    if (!campaign) return;
    
    try {
      setIsSubmitting(true);
      
      // If content was edited, save edits first
      if (isEditing && editedContent) {
        await editCampaignContent(campaign.id, editedContent);
        showToast('Content edits saved', 'success');
      }
      
      // Mark as reviewed with current notes
      await reviewCampaign(campaign.id, 'reviewed', reviewerNotes);
      showToast('Campaign marked as reviewed', 'success');
      
      // Reload campaign to get updated data
      await loadCampaign();
      setIsEditing(false);
    } catch (err) {
      console.error('Error marking as reviewed:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to mark as reviewed';
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading message="Loading campaign for review..." />
        </div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-red-600 mb-2">Error Loading Campaign</h3>
            <p className="text-gray-600 mb-4">{error || 'Campaign not found'}</p>
            <button
              onClick={() => navigate('/campaigns')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Back to Campaigns
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentStatus = REVIEW_STATUS_OPTIONS.find(s => s.value === campaign.review_status) || REVIEW_STATUS_OPTIONS[0];
  const content = campaign.ai_processing_data?.content || {};
  const displayContent = isEditing && editedContent ? editedContent : content;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Editorial Review
            </h2>
            <p className="text-gray-600">
              {campaign.campaign_name} • {campaign.advertiser_name}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${currentStatus.color}`}>
              {currentStatus.label}
            </span>
            <button
              onClick={() => navigate('/campaigns')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Back to Campaigns
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Preview */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Email Preview</h3>
              <button
                onClick={() => navigate(`/preview/${campaign.id}`)}
                className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
              >
                View Full Preview →
              </button>
            </div>
            <PreviewFrame
              html={previewHtml || '<p>Preview not available. Please ensure the campaign has been processed and proof generated.</p>'}
              title="Email Preview"
            />
          </div>

          {/* Content Review Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Content Review</h3>
              <button
                onClick={() => {
                  setIsEditing(!isEditing);
                  if (!isEditing && !editedContent) {
                    setEditedContent({ ...content });
                  }
                }}
                className={`px-3 py-1 text-sm rounded ${
                  isEditing 
                    ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                    : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                }`}
              >
                {isEditing ? '✓ Editing' : 'Edit Content'}
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject Line
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedContent?.subject_line || ''}
                    onChange={(e) => handleContentEdit('subject_line', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="px-3 py-2 bg-gray-50 rounded-lg text-gray-900">
                    {displayContent?.subject_line || '—'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preview Text
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedContent?.preview_text || ''}
                    onChange={(e) => handleContentEdit('preview_text', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="px-3 py-2 bg-gray-50 rounded-lg text-gray-900">
                    {displayContent?.preview_text || '—'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Headline
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedContent?.headline || ''}
                    onChange={(e) => handleContentEdit('headline', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="px-3 py-2 bg-gray-50 rounded-lg text-gray-900">
                    {displayContent?.headline || '—'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Body Copy
                </label>
                {isEditing ? (
                  <textarea
                    value={editedContent?.body_copy || ''}
                    onChange={(e) => handleContentEdit('body_copy', e.target.value)}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="px-3 py-2 bg-gray-50 rounded-lg text-gray-900 whitespace-pre-wrap">
                    {displayContent?.body_copy || '—'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CTA Text
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedContent?.cta_text || ''}
                    onChange={(e) => handleContentEdit('cta_text', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                ) : (
                  <p className="px-3 py-2 bg-gray-50 rounded-lg text-gray-900">
                    {displayContent?.cta_text || '—'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Review Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Review Panel</h3>

            {/* Review Status */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Status
              </label>
              <select
                value={reviewStatus}
                onChange={(e) => setReviewStatus(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {REVIEW_STATUS_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Quick Action: Mark as Reviewed */}
            {campaign.review_status !== 'reviewed' && (
              <button
                onClick={handleMarkAsReviewed}
                disabled={isSubmitting}
                className="w-full px-4 py-2 mb-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isSubmitting ? 'Processing...' : 'Mark as Reviewed'}
              </button>
            )}

            {/* Reviewer Notes */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reviewer Notes
              </label>
              <textarea
                value={reviewerNotes}
                onChange={(e) => setReviewerNotes(e.target.value)}
                rows={6}
                placeholder="Add your review notes here..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                {reviewerNotes.length}/2000 characters
              </p>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleReviewSubmit}
              disabled={isSubmitting}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Review'}
            </button>

            {/* Campaign Details */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <CampaignDetails campaign={campaign} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReviewPage;

