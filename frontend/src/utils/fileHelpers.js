/**
 * Utility functions for handling files, including downloading from URLs
 */

/**
 * Download a file from a URL and convert it to a File object
 * @param {string} url - URL to download from (presigned URL)
 * @param {string} filename - Name for the file
 * @param {string} mimeType - MIME type of the file
 * @returns {Promise<File>} File object
 */
export async function urlToFile(url, filename, mimeType) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    const file = new File([blob], filename, { type: mimeType || blob.type });
    return file;
  } catch (error) {
    console.error('Error converting URL to file:', error);
    throw error;
  }
}

/**
 * Load existing files from campaign ai_processing_data
 * @param {Object} aiProcessingData - ai_processing_data from campaign
 * @returns {Promise<{logo: File[], heroImages: File[]}>} Object with logo and heroImages arrays
 */
export async function loadExistingFiles(aiProcessingData) {
  const logo = [];
  const heroImages = [];
  
  if (!aiProcessingData) {
    return { logo, heroImages };
  }
  
  // Load logo if available
  if (aiProcessingData.logo && aiProcessingData.logo.presigned_url) {
    try {
      const logoFile = await urlToFile(
        aiProcessingData.logo.presigned_url,
        aiProcessingData.logo.filename || 'logo.png',
        aiProcessingData.logo.content_type || 'image/png'
      );
      logo.push(logoFile);
    } catch (error) {
      console.error('Error loading logo:', error);
    }
  }
  
  // Load hero images if available
  if (aiProcessingData.hero_images && Array.isArray(aiProcessingData.hero_images)) {
    for (const heroImg of aiProcessingData.hero_images) {
      if (heroImg && heroImg.presigned_url) {
        try {
          const heroFile = await urlToFile(
            heroImg.presigned_url,
            heroImg.filename || 'hero.jpg',
            heroImg.content_type || 'image/jpeg'
          );
          heroImages.push(heroFile);
        } catch (error) {
          console.error('Error loading hero image:', error);
        }
      }
    }
  }
  
  return { logo, heroImages };
}

