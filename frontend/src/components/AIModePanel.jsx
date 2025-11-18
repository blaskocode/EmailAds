/**
 * AI Mode Panel - Component for prompt-based campaign generation
 */
function AIModePanel({ aiPrompt, setAiPrompt, generating, aiError, onGenerate }) {
  return (
    <div className="mb-6 p-6 bg-gradient-to-br from-hibid-blue-50 to-hibid-blue-100 border border-hibid-blue-200 rounded-xl shadow-hibid">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-hibid-gray-900 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2 text-hibid-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          AI Campaign Generator
        </h3>
        <p className="text-sm text-hibid-gray-600">
          Describe your campaign in natural language and we'll auto-populate the form for you.
        </p>
      </div>
      
      <textarea
        value={aiPrompt}
        onChange={(e) => {
          setAiPrompt(e.target.value);
        }}
        placeholder="Example: Create a campaign for Acme Corp's Black Friday sale. 30% off all products. Use code BLACKFRIDAY30."
        className="w-full px-4 py-3 border border-hibid-gray-300 rounded-lg focus:ring-2 focus:ring-hibid-blue-500 focus:border-hibid-blue-500 resize-none mb-4"
        rows={4}
        disabled={generating}
      />
      
      {aiError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{aiError}</p>
        </div>
      )}
      
      <div className="flex items-center justify-between">
        <div className="text-xs text-hibid-gray-500">
          <p className="mb-1"><strong>Example prompts:</strong></p>
          <ul className="list-disc list-inside space-y-0.5">
            <li>"Promote our summer collection sale. 50% off swimwear. Free shipping over $50."</li>
            <li>"TechStart's new product launch: CloudSync, a cloud storage solution for businesses."</li>
          </ul>
        </div>
        <button
          type="button"
          onClick={onGenerate}
          disabled={generating || !aiPrompt.trim()}
          className="px-6 py-2.5 bg-gradient-hibid text-white rounded-lg font-semibold hover:shadow-hibid-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-hibid flex items-center"
        >
          {generating ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating...
            </>
          ) : (
            <>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Campaign
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default AIModePanel;

