/**
 * PreviewFrame component - Renders HTML email in an iframe
 * Uses srcdoc to inject HTML securely without needing allow-same-origin
 */
function PreviewFrame({ html, width = '600px', title = 'Email Preview' }) {
  if (!html) {
    return (
      <div 
        className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center"
        style={{ width, minHeight: '400px' }}
      >
        <p className="text-gray-500">No preview available</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div 
        className="bg-gray-100 border-2 border-gray-300 rounded-lg overflow-hidden shadow-lg"
        style={{ width }}
      >
        <iframe
          title={title}
          className="w-full border-0"
          style={{ 
            minHeight: '600px',
            display: 'block'
          }}
          sandbox="allow-scripts"
          srcDoc={html}
        />
      </div>
    </div>
  );
}

export default PreviewFrame;

