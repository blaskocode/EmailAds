/**
 * Download helper utilities
 */

/**
 * Download HTML file from blob
 * @param {Blob} blob - HTML blob
 * @param {string} filename - Filename for download
 */
export const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      // Use modern clipboard API
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        return successful;
      } catch (err) {
        document.body.removeChild(textArea);
        return false;
      }
    }
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    return false;
  }
};

/**
 * Generate filename for campaign HTML
 * @param {string} campaignName - Campaign name
 * @param {string} campaignId - Campaign ID
 * @returns {string} Filename
 */
export const generateFilename = (campaignName, campaignId) => {
  const safeName = campaignName
    ? campaignName.replace(/[^a-z0-9]/gi, '_').substring(0, 50)
    : 'campaign';
  const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
  return `${safeName}_${date}.html`;
};

