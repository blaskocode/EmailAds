/**
 * Preview page - Shows desktop and mobile preview of email campaign
 */
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import PreviewFrame from '../components/PreviewFrame';
import CampaignDetails from '../components/CampaignDetails';
import ApprovalButtons from '../components/ApprovalButtons';
import RecommendationsPanel from '../components/RecommendationsPanel';
import { getPreview, generateProof, processCampaign, getCampaignStatus, editCampaignContent, regenerateProof, replaceCampaignImage, getRecommendations, getCampaignDetail } from '../services/api';

function PreviewPage() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('both'); // 'desktop', 'mobile', 'both'
  const [refreshing, setRefreshing] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false); // Track if we're automatically processing
  const processingRef = useRef(false); // Prevent duplicate processing
  const [isEditing, setIsEditing] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isReplacingImage, setIsReplacingImage] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [campaignStatus, setCampaignStatus] = useState(null);

  useEffect(() => {
    loadPreview();
    loadPerformanceMetrics();
  }, [campaignId]);

  const loadPerformanceMetrics = async () => {
    try {
      const campaign = await getCampaignDetail(campaignId);
      if (campaign) {
        setPerformanceMetrics({
          open_rate: campaign.open_rate,
          click_rate: campaign.click_rate,
          conversion_rate: campaign.conversion_rate,
          performance_score: campaign.performance_score,
          performance_timestamp: campaign.performance_timestamp
        });
        // Store campaign status to control approval buttons visibility
        if (campaign.status) {
          setCampaignStatus(campaign.status);
        }
      }
    } catch (err) {
      // Silently fail - performance metrics are optional
      console.debug('Could not load performance metrics:', err);
    }
  };

  const loadPreview = async () => {
    // Prevent duplicate processing (React StrictMode runs effects twice in dev)
    if (processingRef.current) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // First, check campaign status to avoid unnecessary 400 errors
      const statusResponse = await getCampaignStatus(campaignId);
      
      // Store campaign status for approval buttons visibility
      if (statusResponse.status) {
        setCampaignStatus(statusResponse.status);
      }
      
      // If campaign can't be previewed yet, process and generate first
      if (!statusResponse.can_preview) {
        setIsProcessing(true);
        processingRef.current = true;
        
        try {
          // Step 1: Process campaign (if needed)
          if (statusResponse.status === 'uploaded') {
            try {
              await processCampaign(campaignId);
            } catch (processErr) {
              // Check if it's already processed
              const processErrorMsg = processErr.response?.data?.detail || 
                                     processErr.response?.data?.message || '';
              const alreadyProcessed = processErrorMsg.toLowerCase().includes('already processed') || 
                                      processErrorMsg.toLowerCase().includes('processed') ||
                                      processErr.response?.status === 200;
              
              if (!alreadyProcessed) {
                throw processErr;
              }
            }
          }
          
          // Step 2: Generate proof (if needed)
          if (statusResponse.status !== 'ready') {
            await generateProof(campaignId);
          }
          
          // Step 3: Get preview
          const data = await getPreview(campaignId);
          setPreviewData(data);
          setError(null);
          setIsProcessing(false);
        } catch (genErr) {
          console.error('Error processing/generating preview:', genErr);
          const genErrorMsg = genErr.response?.data?.detail || 
                            genErr.response?.data?.message || 
                            genErr.message;
          setError(genErrorMsg || 'Failed to generate preview. Please try again.');
          setIsProcessing(false);
        } finally {
          processingRef.current = false;
        }
      } else {
        // Campaign is ready, get preview directly
        const data = await getPreview(campaignId);
        setPreviewData(data);
        setError(null);
      }
    } catch (err) {
      console.error('Error loading preview:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load preview';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      // Regenerate proof
      await generateProof(campaignId);
      // Reload preview
      await loadPreview();
    } catch (err) {
      console.error('Error refreshing preview:', err);
      setError(err.response?.data?.detail || 'Failed to refresh preview');
    } finally {
      setRefreshing(false);
    }
  };

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      // Regenerate proof with latest campaign data
      const regeneratedData = await regenerateProof(campaignId);
      // Update preview data
      setPreviewData(regeneratedData);
      setError(null);
    } catch (err) {
      console.error('Error regenerating preview:', err);
      setError(err.response?.data?.detail || err.userMessage || 'Failed to regenerate preview');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSaveEdit = async (editData) => {
    setIsSaving(true);
    try {
      // Save edited content
      await editCampaignContent(campaignId, editData);
      setIsEditing(false);
      // Regenerate preview with new content
      await handleRegenerate();
    } catch (err) {
      console.error('Error saving edit:', err);
      setError(err.response?.data?.detail || err.userMessage || 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleGetRecommendations = async () => {
    try {
      setLoadingRecommendations(true);
      const data = await getRecommendations(campaignId);
      setRecommendations(data);
      setShowRecommendations(true);
    } catch (err) {
      console.error('Error loading recommendations:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to load recommendations';
      alert(errorMessage);
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleApplyRecommendation = async (field, value) => {
    try {
      // Update the field using edit endpoint
      await editCampaignContent(campaignId, { [field]: value });
      
      // Regenerate preview with new content
      await handleRegenerate();
      
      // Close recommendations panel
      setShowRecommendations(false);
      
      // Reload preview to show updated content
      await loadPreview();
    } catch (err) {
      console.error('Error applying recommendation:', err);
      alert('Failed to apply recommendation. Please try again.');
    }
  };

  const handleReplaceImage = async (imageType, file) => {
    setIsReplacingImage(true);
    try {
      // Replace image via API
      await replaceCampaignImage(campaignId, imageType, file);
      // Regenerate preview with new image
      await handleRegenerate();
    } catch (err) {
      console.error('Error replacing image:', err);
      setError(err.response?.data?.detail || err.userMessage || 'Failed to replace image');
    } finally {
      setIsReplacingImage(false);
    }
  };

  if (loading || isProcessing) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-xl shadow-hibid p-8 border border-hibid-gray-200">
          <Loading message={isProcessing ? "Processing campaign..." : "Loading preview..."} />
        </div>
      </div>
    );
  }

  if (error && !isProcessing) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-xl shadow-hibid p-8 border border-hibid-gray-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Preview</h2>
            <p className="text-hibid-gray-600 mb-6">{error}</p>
            <button
              onClick={handleRefresh}
              className="px-6 py-2.5 bg-gradient-hibid text-white rounded-lg hover:shadow-hibid-lg transition-all duration-200 font-semibold shadow-hibid"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!previewData) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-xl shadow-hibid p-8 border border-hibid-gray-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-hibid-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-hibid-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <p className="text-hibid-gray-600 font-medium">No preview data available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 lg:px-6 max-w-7xl">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-hibid p-6 mb-6 border border-hibid-gray-200">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h2 className="text-2xl lg:text-3xl font-bold text-hibid-gray-900 mb-2">
              Campaign Preview
            </h2>
            <p className="text-hibid-gray-600">
              {previewData.metadata?.campaign_name || `Campaign ID: ${campaignId}`}
            </p>
          </div>
          
          {/* Controls */}
          <div className="flex flex-wrap items-center gap-3">
            {/* View Mode Toggle */}
            <div className="flex items-center gap-1 bg-hibid-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('desktop')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
                  viewMode === 'desktop'
                    ? 'bg-white text-hibid-blue-600 shadow-hibid'
                    : 'text-hibid-gray-600 hover:text-hibid-gray-900'
                }`}
              >
                Desktop
              </button>
              <button
                onClick={() => setViewMode('mobile')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
                  viewMode === 'mobile'
                    ? 'bg-white text-hibid-blue-600 shadow-hibid'
                    : 'text-hibid-gray-600 hover:text-hibid-gray-900'
                }`}
              >
                Mobile
              </button>
              <button
                onClick={() => setViewMode('both')}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
                  viewMode === 'both'
                    ? 'bg-white text-hibid-blue-600 shadow-hibid'
                    : 'text-hibid-gray-600 hover:text-hibid-gray-900'
                }`}
              >
                Both
              </button>
            </div>

            {/* Get Recommendations Button */}
            <button
              onClick={handleGetRecommendations}
              disabled={loadingRecommendations}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid hover:shadow-hibid-lg font-medium text-sm"
            >
              {loadingRecommendations ? 'Loading...' : 'Get Recommendations'}
            </button>

            {/* Regenerate Button */}
            <button
              onClick={handleRegenerate}
              disabled={isRegenerating || refreshing}
              className="px-4 py-2 bg-gradient-hibid text-white rounded-lg hover:shadow-hibid-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-hibid font-semibold text-sm"
            >
              {isRegenerating ? 'Regenerating...' : 'Regenerate Preview'}
            </button>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing || isRegenerating}
              className="px-4 py-2 bg-hibid-gray-100 text-hibid-gray-700 rounded-lg hover:bg-hibid-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium text-sm"
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Preview Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Desktop Preview */}
          {(viewMode === 'desktop' || viewMode === 'both') && (
            <div className="bg-white rounded-xl shadow-hibid p-4 border border-hibid-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-hibid-gray-900">Desktop Preview</h3>
                <span className="text-xs text-hibid-gray-500 bg-hibid-gray-100 px-2 py-1 rounded-md">600px width</span>
              </div>
              <PreviewFrame
                html={previewData.html_preview}
                width="600px"
                title="Desktop Email Preview"
              />
            </div>
          )}

          {/* Mobile Preview */}
          {(viewMode === 'mobile' || viewMode === 'both') && (
            <div className="bg-white rounded-xl shadow-hibid p-4 border border-hibid-gray-200">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-hibid-gray-900">Mobile Preview</h3>
                <span className="text-xs text-hibid-gray-500 bg-hibid-gray-100 px-2 py-1 rounded-md">320px width</span>
              </div>
              <PreviewFrame
                html={previewData.html_preview}
                width="320px"
                title="Mobile Email Preview"
              />
            </div>
          )}
        </div>

        {/* Campaign Details Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <CampaignDetails
            metadata={previewData.metadata}
            aiSuggestions={previewData.ai_suggestions}
            isEditing={isEditing}
            onEdit={handleEdit}
            onSave={handleSaveEdit}
            onCancel={handleCancelEdit}
            assets={previewData.assets}
            onReplaceImage={handleReplaceImage}
            isReplacingImage={isReplacingImage}
            performanceMetrics={performanceMetrics}
          />
          
          {/* Approval Buttons */}
          {campaignStatus !== 'approved' && (
            <div className="bg-white rounded-xl shadow-hibid p-6 border border-hibid-gray-200">
              <h3 className="text-lg font-semibold text-hibid-gray-900 mb-4">
                Campaign Actions
              </h3>
              <ApprovalButtons
                campaignId={campaignId}
                onApprovalSuccess={(response) => {
                  navigate(`/success/${campaignId}`, { 
                    state: { approvalData: response } 
                  });
                }}
              />
            </div>
          )}
          {campaignStatus === 'approved' && (
            <div className="bg-white rounded-xl shadow-hibid p-6 border border-hibid-gray-200">
              <h3 className="text-lg font-semibold text-hibid-gray-900 mb-4">
                Campaign Status
              </h3>
              <div className="bg-green-50 border border-green-200 rounded-xl p-4 shadow-hibid">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <p className="text-green-800 font-semibold">Campaign Approved</p>
                </div>
                <p className="text-green-700 text-sm mt-2">
                  This campaign has been approved and the final HTML has been generated.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations Panel */}
      {showRecommendations && (
        <RecommendationsPanel
          recommendations={recommendations}
          onApplyRecommendation={handleApplyRecommendation}
          onClose={() => setShowRecommendations(false)}
        />
      )}
    </div>
  );
}

export default PreviewPage;
