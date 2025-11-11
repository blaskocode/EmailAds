/**
 * Upload page - Main entry point for creating campaigns
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FormInput from '../components/FormInput';
import FileUpload from '../components/FileUpload';
import Loading from '../components/Loading';
import { uploadCampaign } from '../services/api';

function UploadPage() {
  const navigate = useNavigate();
  
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
  const [error, setError] = useState(null);
  const [errors, setErrors] = useState({});

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

      // Add logo (required)
      formDataToSend.append('logo', logo[0]);

      // Add hero images (optional)
      heroImages.forEach((heroImg, index) => {
        formDataToSend.append('hero_images', heroImg);
      });

      // Upload to API
      const response = await uploadCampaign(formDataToSend);
      
      // Redirect to preview page
      navigate(`/preview/${response.campaign_id}`);
      
    } catch (err) {
      console.error('Upload error:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('Failed to upload campaign. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <Loading message="Uploading campaign assets..." size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Create New Campaign
        </h2>
        <p className="text-gray-600 mb-8">
          Upload your assets and we'll generate a professional email campaign for you.
        </p>

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
              Upload & Create Campaign
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default UploadPage;
