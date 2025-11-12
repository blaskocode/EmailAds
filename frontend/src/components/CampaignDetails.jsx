/**
 * CampaignDetails component - Displays campaign metadata and AI suggestions
 * Supports editing mode for inline content editing
 */
import { useState, useEffect } from 'react';

function CampaignDetails({ metadata, aiSuggestions, onEdit, isEditing = false, onSave, onCancel, assets, onReplaceImage, isReplacingImage = false }) {
  const [editData, setEditData] = useState({
    subject_line: '',
    preview_text: '',
    headline: '',
    body_copy: '',
    cta_text: '',
    cta_url: '',
    footer_text: ''
  });

  // Update editData when metadata/aiSuggestions change
  useEffect(() => {
    setEditData({
      subject_line: metadata?.subject_line || '',
      preview_text: metadata?.preview_text || '',
      headline: aiSuggestions?.headline || '',
      body_copy: aiSuggestions?.body_paragraphs?.join('\n\n') || '',
      cta_text: aiSuggestions?.cta_text || '',
      cta_url: metadata?.cta_url || '',
      footer_text: metadata?.footer_text || ''
    });
  }, [metadata, aiSuggestions]);

  if (!metadata && !aiSuggestions) {
    return null;
  }

  const handleFieldChange = (field, value) => {
    setEditData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave(editData);
    }
  };

  const handleCancel = () => {
    // Reset to original values
    setEditData({
      subject_line: metadata?.subject_line || '',
      preview_text: metadata?.preview_text || '',
      headline: aiSuggestions?.headline || '',
      body_copy: aiSuggestions?.body_paragraphs?.join('\n\n') || '',
      cta_text: aiSuggestions?.cta_text || '',
      cta_url: metadata?.cta_url || '',
      footer_text: metadata?.footer_text || ''
    });
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
      <div className="flex items-center justify-between border-b pb-2">
        <h3 className="text-xl font-semibold text-gray-900">
          Campaign Details
        </h3>
        {!isEditing && onEdit && (
          <button
            onClick={onEdit}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Edit
          </button>
        )}
        {isEditing && (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Campaign Metadata */}
      {metadata && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Campaign Name
            </label>
            <p className="text-gray-900">{metadata.campaign_name || 'N/A'}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Advertiser
            </label>
            <p className="text-gray-900">{metadata.advertiser_name || 'N/A'}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject Line
            </label>
            {isEditing ? (
              <input
                type="text"
                value={editData.subject_line}
                onChange={(e) => handleFieldChange('subject_line', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                maxLength={200}
              />
            ) : (
              <p className="text-gray-900">{metadata.subject_line || 'N/A'}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preview Text
            </label>
            {isEditing ? (
              <input
                type="text"
                value={editData.preview_text}
                onChange={(e) => handleFieldChange('preview_text', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                maxLength={200}
              />
            ) : (
              <p className="text-gray-600 text-sm">{metadata.preview_text || 'N/A'}</p>
            )}
          </div>

          {metadata.generated_at && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Generated At
              </label>
              <p className="text-gray-600 text-sm">
                {new Date(metadata.generated_at).toLocaleString()}
              </p>
            </div>
          )}

          {metadata.feedback && (
            <div className="pt-4 border-t">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feedback
              </label>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{metadata.feedback}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI Suggestions */}
      {aiSuggestions && (
        <div className="space-y-4 pt-4 border-t">
          <h4 className="text-lg font-semibold text-gray-900">AI Suggestions</h4>

          {aiSuggestions.subject_lines && aiSuggestions.subject_lines.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subject Line Variations
              </label>
              <ul className="space-y-2">
                {aiSuggestions.subject_lines.map((subject, idx) => (
                  <li key={idx} className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                    {subject}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {aiSuggestions.headline && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Optimized Headline
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.headline}
                  onChange={(e) => handleFieldChange('headline', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={200}
                />
              ) : (
                <p className="text-gray-900">{aiSuggestions.headline}</p>
              )}
            </div>
          )}

          {aiSuggestions.body_paragraphs && aiSuggestions.body_paragraphs.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Optimized Body Copy
              </label>
              {isEditing ? (
                <textarea
                  value={editData.body_copy}
                  onChange={(e) => handleFieldChange('body_copy', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  maxLength={5000}
                />
              ) : (
                <div className="space-y-2">
                  {aiSuggestions.body_paragraphs.map((paragraph, idx) => (
                    <p key={idx} className="text-sm text-gray-700">
                      {paragraph}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}

          {aiSuggestions.cta_text && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CTA Text
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.cta_text}
                  onChange={(e) => handleFieldChange('cta_text', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={50}
                />
              ) : (
                <p className="text-gray-900 font-medium">{aiSuggestions.cta_text}</p>
              )}
            </div>
          )}

          {aiSuggestions.suggestions && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Additional Suggestions
              </label>
              <p className="text-sm text-gray-600 italic">{aiSuggestions.suggestions}</p>
            </div>
          )}

          {aiSuggestions.image_alt_texts && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Image Alt Texts
              </label>
              <div className="space-y-2">
                {aiSuggestions.image_alt_texts.logo && (
                  <div>
                    <span className="text-xs font-medium text-gray-500">Logo: </span>
                    <span className="text-sm text-gray-700">{aiSuggestions.image_alt_texts.logo}</span>
                  </div>
                )}
                {aiSuggestions.image_alt_texts.hero_images && 
                 aiSuggestions.image_alt_texts.hero_images.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-500">Hero Images: </span>
                    <ul className="mt-1 space-y-1">
                      {aiSuggestions.image_alt_texts.hero_images.map((alt, idx) => (
                        <li key={idx} className="text-sm text-gray-700">
                          {idx + 1}. {alt}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Image Management Section */}
      {assets && (assets.logo_url || (assets.hero_image_urls && assets.hero_image_urls.length > 0)) && (
        <div className="space-y-4 pt-4 border-t">
          <h4 className="text-lg font-semibold text-gray-900">Images</h4>
          
          {/* Logo */}
          {assets.logo_url && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Logo
              </label>
              <div className="relative group">
                <img
                  src={assets.logo_url}
                  alt="Campaign logo"
                  className={`w-full max-w-[200px] h-auto border border-gray-300 rounded-lg ${isReplacingImage ? 'opacity-50' : ''}`}
                />
                {isReplacingImage && (
                  <div className="absolute inset-0 bg-gray-200 bg-opacity-75 rounded-lg flex items-center justify-center">
                    <div className="text-sm text-gray-700 font-medium">Replacing...</div>
                  </div>
                )}
                {onReplaceImage && !isReplacingImage && (
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 rounded-lg transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <label className="px-3 py-1 bg-white text-gray-700 rounded cursor-pointer hover:bg-gray-100 text-sm font-medium">
                      Replace
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/jpg"
                        className="hidden"
                        disabled={isReplacingImage}
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file && onReplaceImage && !isReplacingImage) {
                            onReplaceImage('logo', file);
                          }
                          // Reset input so same file can be selected again
                          e.target.value = '';
                        }}
                      />
                    </label>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Hero Images */}
          {assets.hero_image_urls && assets.hero_image_urls.length > 0 && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Hero Images
              </label>
              <div className="grid grid-cols-1 gap-3">
                {assets.hero_image_urls.map((url, idx) => (
                  <div key={idx} className="relative group">
                    <img
                      src={url}
                      alt={`Hero image ${idx + 1}`}
                      className={`w-full h-auto border border-gray-300 rounded-lg ${isReplacingImage ? 'opacity-50' : ''}`}
                    />
                    {isReplacingImage && (
                      <div className="absolute inset-0 bg-gray-200 bg-opacity-75 rounded-lg flex items-center justify-center">
                        <div className="text-sm text-gray-700 font-medium">Replacing...</div>
                      </div>
                    )}
                    {onReplaceImage && !isReplacingImage && (
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 rounded-lg transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                        <label className="px-3 py-1 bg-white text-gray-700 rounded cursor-pointer hover:bg-gray-100 text-sm font-medium">
                          Replace
                          <input
                            type="file"
                            accept="image/png,image/jpeg,image/jpg"
                            className="hidden"
                            disabled={isReplacingImage}
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file && onReplaceImage && !isReplacingImage) {
                                onReplaceImage(`hero_${idx}`, file);
                              }
                              // Reset input so same file can be selected again
                              e.target.value = '';
                            }}
                          />
                        </label>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CampaignDetails;

