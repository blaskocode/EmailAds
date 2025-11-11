/**
 * Upload page - Main entry point for creating campaigns
 */
import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import FormInput from '../components/FormInput';
import FileUpload from '../components/FileUpload';
import Loading from '../components/Loading';
import { uploadCampaign, getCampaignDetail } from '../services/api';
import { loadExistingFiles } from '../utils/fileHelpers';

function UploadPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Form state
  const [formData, setFormData] = useState({
    campaign_name: '',
    advertiser_name: '',
    subject_line: '',
    preview_text: '',
    body_copy: '',
    cta_text: '',
    cta_url: '',
    footer_text: ''
  });

  // File state
  const [logo, setLogo] = useState([]);
  const [heroImages, setHeroImages] = useState([]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [loadingCampaign, setLoadingCampaign] = useState(false);
  const [error, setError] = useState(null);
  const [errors, setErrors] = useState({});
  const [editingCampaignId, setEditingCampaignId] = useState(null);
  const [hasExistingFiles, setHasExistingFiles] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);

  // Load campaign data if editing
  useEffect(() => {
    const editCampaignId = location.state?.editCampaignId;
    if (editCampaignId) {
      loadCampaignForEditing(editCampaignId);
    }
  }, [location.state]);

  const loadCampaignForEditing = async (campaignId) => {
    try {
      setLoadingCampaign(true);
      setLoadingFiles(true);
      setError(null);
      setEditingCampaignId(campaignId);
      
      const campaign = await getCampaignDetail(campaignId);
      
      // Pre-fill form with campaign data
      const contentData = campaign.ai_processing_data?.content || {};
      setFormData({
        campaign_name: campaign.campaign_name || '',
        advertiser_name: campaign.advertiser_name || '',
        subject_line: contentData.subject_line || '',
        preview_text: contentData.preview_text || '',
        body_copy: contentData.body_copy || '',
        cta_text: contentData.cta_text || '',
        cta_url: contentData.cta_url || '',
        footer_text: contentData.footer_text || ''
      });
      
      // Load existing files from ai_processing_data
      if (campaign.ai_processing_data) {
        setHasExistingFiles(true);
        try {
          const { logo: loadedLogo, heroImages: loadedHeroImages } = await loadExistingFiles(campaign.ai_processing_data);
          if (loadedLogo.length > 0) {
            setLogo(loadedLogo);
          }
          if (loadedHeroImages.length > 0) {
            setHeroImages(loadedHeroImages);
          }
        } catch (fileError) {
          console.error('Error loading existing files:', fileError);
          // Don't fail the whole operation if files can't be loaded
          setError('Warning: Could not load existing files. You may need to re-upload them.');
        }
      } else if (campaign.assets_s3_path) {
        setHasExistingFiles(true);
      }
      
    } catch (err) {
      console.error('Error loading campaign for editing:', err);
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'Failed to load campaign data';
      setError(errorMessage);
      // Clear edit mode on error
      setEditingCampaignId(null);
    } finally {
      setLoadingCampaign(false);
      setLoadingFiles(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.campaign_name.trim()) {
      newErrors.campaign_name = 'Campaign name is required';
    }
    if (!formData.advertiser_name.trim()) {
      newErrors.advertiser_name = 'Advertiser name is required';
    }
    
    // Logo validation: always required (existing files should be loaded when editing)
    if (logo.length === 0) {
      newErrors.logo = 'Logo is required';
    }

    // Hero images validation (optional but if provided, max 3)
    if (heroImages.length > 3) {
      newErrors.heroImages = 'Maximum 3 hero images allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setErrors({});

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Build FormData
      const formDataToSend = new FormData();
      
      // Add text fields
      Object.keys(formData).forEach(key => {
        if (formData[key]) {
          formDataToSend.append(key, formData[key]);
        }
      });
      
      // Add campaign_id if editing (to update existing campaign instead of creating new)
      if (editingCampaignId) {
        formDataToSend.append('campaign_id', editingCampaignId);
      }

      // Add logo (required - use existing if editing, or new if uploaded)
      if (logo.length === 0) {
        // This should not happen if validation passed, but handle gracefully
        throw new Error('Logo is required. Please upload a logo file.');
      }
      formDataToSend.append('logo', logo[0]);

      // Add hero images (only if provided)
      heroImages.forEach((heroImg, index) => {
        formDataToSend.append('hero_images', heroImg);
      });

      // Upload to API
      const response = await uploadCampaign(formDataToSend);
      
      // Redirect to preview page
      navigate(`/preview/${response.campaign_id}`);
      
    } catch (err) {
      console.error('Upload error:', err);
      // Extract error message from various possible error formats
      let errorMessage = 'Failed to upload campaign. Please try again.';
      
      if (err.response?.data) {
        // FastAPI error format
        if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('Error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading || loadingCampaign || loadingFiles) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading 
            message={
              loadingFiles 
                ? "Loading existing files..." 
                : loadingCampaign 
                ? "Loading campaign data..." 
                : "Uploading campaign assets..."
            } 
            size="lg" 
          />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {editingCampaignId ? 'Edit Campaign' : 'Create New Campaign'}
        </h2>
        <p className="text-gray-600 mb-8">
          {editingCampaignId 
            ? 'Update your campaign details and assets. Upload new files to replace existing ones.'
            : "Upload your assets and we'll generate a professional email campaign for you."}
        </p>
        
        {editingCampaignId && hasExistingFiles && logo.length === 0 && heroImages.length === 0 && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Existing files are being loaded. If they don't appear, you may need to re-upload them.
            </p>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Campaign Information */}
          <div className="border-b border-gray-200 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Campaign Information
            </h3>
            
            <FormInput
              label="Campaign Name"
              name="campaign_name"
              value={formData.campaign_name}
              onChange={handleInputChange}
              placeholder="e.g., Fall Sale 2025"
              required
              error={errors.campaign_name}
              maxLength={200}
            />

            <FormInput
              label="Advertiser Name"
              name="advertiser_name"
              value={formData.advertiser_name}
              onChange={handleInputChange}
              placeholder="e.g., Acme Corp"
              required
              error={errors.advertiser_name}
              maxLength={200}
            />
          </div>

          {/* Assets Upload */}
          <div className="border-b border-gray-200 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Assets
            </h3>

            <FileUpload
              label="Logo"
              files={logo}
              onFilesChange={setLogo}
              maxFiles={1}
              required
              error={errors.logo}
            />

            <FileUpload
              label="Hero Images (Optional, up to 3)"
              files={heroImages}
              onFilesChange={setHeroImages}
              maxFiles={3}
              error={errors.heroImages}
            />
          </div>

          {/* Email Content */}
          <div className="border-b border-gray-200 pb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Email Content
            </h3>

            <FormInput
              label="Subject Line"
              name="subject_line"
              value={formData.subject_line}
              onChange={handleInputChange}
              placeholder="e.g., 50% Off Fall Collection!"
              error={errors.subject_line}
              maxLength={200}
            />

            <FormInput
              label="Preview Text"
              name="preview_text"
              value={formData.preview_text}
              onChange={handleInputChange}
              placeholder="Short preview text (50-90 characters)"
              error={errors.preview_text}
              maxLength={200}
            />

            <FormInput
              label="Body Copy"
              name="body_copy"
              type="textarea"
              value={formData.body_copy}
              onChange={handleInputChange}
              placeholder="Main email content..."
              error={errors.body_copy}
              maxLength={5000}
              rows={6}
            />

            <FormInput
              label="CTA Button Text"
              name="cta_text"
              value={formData.cta_text}
              onChange={handleInputChange}
              placeholder="e.g., Shop Now"
              error={errors.cta_text}
              maxLength={50}
            />

            <FormInput
              label="CTA Button URL"
              name="cta_url"
              type="url"
              value={formData.cta_url}
              onChange={handleInputChange}
              placeholder="https://example.com/shop"
              error={errors.cta_url}
              maxLength={500}
            />

            <FormInput
              label="Footer Text (Optional)"
              name="footer_text"
              value={formData.footer_text}
              onChange={handleInputChange}
              placeholder="Footer content..."
              error={errors.footer_text}
              maxLength={500}
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-6">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {editingCampaignId ? 'Update & Resubmit Campaign' : 'Upload & Create Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default UploadPage;
