/**
 * RecommendationsPanel component - Displays AI-based content recommendations
 */
import { useState } from 'react';

function RecommendationsPanel({ recommendations, onApplyRecommendation, onClose }) {
  const [selectedCategory, setSelectedCategory] = useState('subject_lines');

  if (!recommendations) {
    return null;
  }

  const categories = {
    subject_lines: {
      title: 'Subject Lines',
      items: recommendations.subject_line_recommendations || [],
      field: 'subject_line'
    },
    preview_texts: {
      title: 'Preview Texts',
      items: recommendations.preview_text_recommendations || [],
      field: 'preview_text'
    },
    cta_texts: {
      title: 'CTA Texts',
      items: recommendations.cta_text_recommendations || [],
      field: 'cta_text'
    }
  };

  const handleApply = (item, field) => {
    if (onApplyRecommendation) {
      onApplyRecommendation(field, item.content);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Recommendations</h2>
            {recommendations.historical_data_available && (
              <p className="text-sm text-gray-600 mt-1">
                Based on {recommendations.total_campaigns_analyzed} high-performing campaigns
              </p>
            )}
            {!recommendations.historical_data_available && (
              <p className="text-sm text-gray-500 mt-1 italic">
                Limited historical data available. Recommendations are based on general best practices.
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Category Tabs */}
          <div className="flex gap-2 mb-6 border-b">
            {Object.entries(categories).map(([key, category]) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  selectedCategory === key
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {category.title}
              </button>
            ))}
          </div>

          {/* Recommendations List */}
          <div className="space-y-4">
            {categories[selectedCategory].items.length > 0 ? (
              categories[selectedCategory].items.map((item, idx) => (
                <div
                  key={idx}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-gray-900 font-medium mb-2">{item.content}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Confidence:</span>
                          <span className="text-blue-600 font-semibold">
                            {(item.confidence_score * 100).toFixed(0)}%
                          </span>
                        </span>
                        {item.based_on_count && (
                          <span className="flex items-center gap-1">
                            <span className="font-medium">Based on:</span>
                            <span>{item.based_on_count} campaigns</span>
                          </span>
                        )}
                      </div>
                      {item.reasoning && (
                        <p className="text-sm text-gray-500 mt-2 italic">{item.reasoning}</p>
                      )}
                    </div>
                    <button
                      onClick={() => handleApply(item, categories[selectedCategory].field)}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium whitespace-nowrap"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No recommendations available for this category.</p>
              </div>
            )}
          </div>

          {/* Additional Suggestions */}
          {(recommendations.content_structure_suggestions || recommendations.image_optimization_suggestions) && (
            <div className="mt-8 pt-6 border-t space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Additional Suggestions</h3>
              
              {recommendations.content_structure_suggestions && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Content Structure</h4>
                  <p className="text-sm text-blue-800">{recommendations.content_structure_suggestions}</p>
                </div>
              )}
              
              {recommendations.image_optimization_suggestions && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h4 className="font-medium text-purple-900 mb-2">Image Optimization</h4>
                  <p className="text-sm text-purple-800">{recommendations.image_optimization_suggestions}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default RecommendationsPanel;

