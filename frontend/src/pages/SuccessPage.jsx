/**
 * Success page - Shown after campaign approval
 */
import { useState } from 'react';
import { useParams, useLocation, Link, useNavigate } from 'react-router-dom';
import { downloadCampaign } from '../services/api';
import { downloadBlob, copyToClipboard, generateFilename } from '../utils/downloadHelpers';
import Loading from '../components/Loading';

function SuccessPage() {
  const { campaignId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [htmlContent, setHtmlContent] = useState(null);
  
  const approvalData = location.state?.approvalData;
  const campaignName = approvalData?.metadata?.campaign_name || 'campaign';

  const handleDownload = async () => {
    try {
      setDownloading(true);
      setDownloadError(null);
      
      // Get download URL from approval response or fetch from API
      let downloadUrl = approvalData?.download_url;
      
      if (downloadUrl) {
        // Use presigned URL directly - fetch as blob
        const response = await fetch(downloadUrl);
        const blob = await response.blob();
        const filename = generateFilename(campaignName, campaignId);
        downloadBlob(blob, filename);
      } else {
        // Fallback: use download endpoint
        const blob = await downloadCampaign(campaignId);
        const filename = generateFilename(campaignName, campaignId);
        downloadBlob(blob, filename);
        
        // Store HTML content for copy functionality
        const text = await blob.text();
        setHtmlContent(text);
      }
    } catch (err) {
      console.error('Error downloading campaign:', err);
      setDownloadError(err.response?.data?.detail || 'Failed to download HTML');
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyToClipboard = async () => {
    try {
      // Get HTML content if not already loaded
      let html = htmlContent;
      
      if (!html) {
        const downloadUrl = approvalData?.download_url;
        if (downloadUrl) {
          const response = await fetch(downloadUrl);
          html = await response.text();
        } else {
          const blob = await downloadCampaign(campaignId);
          html = await blob.text();
        }
        setHtmlContent(html);
      }
      
      const success = await copyToClipboard(html);
      if (success) {
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 3000);
      } else {
        setDownloadError('Failed to copy to clipboard');
      }
    } catch (err) {
      console.error('Error copying to clipboard:', err);
      setDownloadError('Failed to copy HTML to clipboard');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Campaign Approved!
          </h2>
          <p className="text-gray-600 mb-8">
            Your email campaign has been successfully generated and is ready for use.
          </p>
        </div>

        <div className="space-y-6">
          {approvalData?.message && (
            <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
              {approvalData.message}
            </div>
          )}

          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Download Your Email HTML
            </h3>
            <p className="text-sm text-gray-600">
              Your production-ready email HTML is ready to download. This file can be used directly in your email service provider.
            </p>
            
            {downloadError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {downloadError}
              </div>
            )}

            {copySuccess && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
                HTML copied to clipboard!
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
              >
                {downloading ? (
                  <span className="flex items-center justify-center">
                    <Loading size="sm" message="" />
                    <span className="ml-2">Downloading...</span>
                  </span>
                ) : (
                  'Download HTML File'
                )}
              </button>
              
              <button
                onClick={handleCopyToClipboard}
                disabled={downloading}
                className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
              >
                Copy HTML
              </button>
            </div>
          </div>

          <div className="pt-6 border-t space-y-3">
            <button
              onClick={() => navigate(`/preview/${campaignId}`)}
              className="w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              View Preview Again
            </button>
            
            <Link
              to="/campaigns"
              className="block w-full bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              View All Campaigns
            </Link>
            
            <Link
              to="/"
              className="block w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Create New Campaign
            </Link>
          </div>

          <div className="pt-4">
            <p className="text-xs text-gray-500">
              Campaign ID: {campaignId}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SuccessPage;
