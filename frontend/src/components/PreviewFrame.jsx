/**
 * PreviewFrame component - Renders HTML email in an iframe
 */
import { useEffect, useRef } from 'react';

function PreviewFrame({ html, width = '600px', title = 'Email Preview' }) {
  const iframeRef = useRef(null);

  useEffect(() => {
    if (iframeRef.current && html) {
      const iframe = iframeRef.current;
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      
      // Write HTML to iframe
      iframeDoc.open();
      iframeDoc.write(html);
      iframeDoc.close();
    }
  }, [html]);

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
          ref={iframeRef}
          title={title}
          className="w-full border-0"
          style={{ 
            minHeight: '600px',
            display: 'block'
          }}
          sandbox="allow-same-origin allow-scripts"
        />
      </div>
    </div>
  );
}

export default PreviewFrame;

