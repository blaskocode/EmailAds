/**
 * Preview page - Shows desktop and mobile preview of email campaign
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Loading from '../components/Loading';
import PreviewFrame from '../components/PreviewFrame';
import CampaignDetails from '../components/CampaignDetails';
import ApprovalButtons from '../components/ApprovalButtons';
import { getPreview, generateProof, processCampaign } from '../services/api';

function PreviewPage() {
  const { campaignId } = useParams();
  const navigate = useNavigate();
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('both'); // 'desktop', 'mobile', 'both'
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPreview();
  }, [campaignId]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Try to get preview data
      const data = await getPreview(campaignId);
      setPreviewData(data);
    } catch (err) {
      console.error('Error loading preview:', err);
      
      // If preview doesn't exist, process and generate proof first
      if (err.response?.status === 400 || err.response?.status === 404) {
        try {
          // Step 1: Process campaign (AI processing)
          try {
            await processCampaign(campaignId);
          } catch (processErr) {
            // If already processed, that's okay - continue to generate
            if (processErr.response?.status !== 400) {
              throw processErr;
            }
          }
          
          // Step 2: Generate proof
          await generateProof(campaignId);
          
          // Step 3: Get preview
          const data = await getPreview(campaignId);
          setPreviewData(data);
        } catch (genErr) {
          console.error('Error processing/generating preview:', genErr);
          setError(genErr.response?.data?.detail || 'Failed to generate preview. Please try again.');
        }
      } else {
        setError(err.response?.data?.detail || 'Failed to load preview');
      }
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

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading message="Loading preview..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Preview</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
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
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <p className="text-gray-600">No preview data available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Campaign Preview
            </h2>
            <p className="text-gray-600">
              {previewData.metadata?.campaign_name || `Campaign ID: ${campaignId}`}
            </p>
          </div>
          
          {/* Controls */}
          <div className="flex items-center gap-4">
            {/* View Mode Toggle */}
            <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('desktop')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  viewMode === 'desktop'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Desktop
              </button>
              <button
                onClick={() => setViewMode('mobile')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  viewMode === 'mobile'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Mobile
              </button>
              <button
                onClick={() => setViewMode('both')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  viewMode === 'both'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Both
              </button>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
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
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900">Desktop Preview</h3>
                <span className="text-xs text-gray-500">600px width</span>
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
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-gray-900">Mobile Preview</h3>
                <span className="text-xs text-gray-500">320px width</span>
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
          />
          
          {/* Approval Buttons */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
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
        </div>
      </div>
    </div>
  );
}

export default PreviewPage;
