/**
 * CampaignDetails component - Displays campaign metadata and AI suggestions
 */
function CampaignDetails({ metadata, aiSuggestions }) {
  if (!metadata && !aiSuggestions) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
      <h3 className="text-xl font-semibold text-gray-900 border-b pb-2">
        Campaign Details
      </h3>

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
            <p className="text-gray-900">{metadata.subject_line || 'N/A'}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preview Text
            </label>
            <p className="text-gray-600 text-sm">{metadata.preview_text || 'N/A'}</p>
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
              <p className="text-gray-900">{aiSuggestions.headline}</p>
            </div>
          )}

          {aiSuggestions.body_paragraphs && aiSuggestions.body_paragraphs.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Optimized Body Copy
              </label>
              <div className="space-y-2">
                {aiSuggestions.body_paragraphs.map((paragraph, idx) => (
                  <p key={idx} className="text-sm text-gray-700">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          )}

          {aiSuggestions.cta_text && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CTA Text
              </label>
              <p className="text-gray-900 font-medium">{aiSuggestions.cta_text}</p>
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
    </div>
  );
}

export default CampaignDetails;

