/**
 * Utilities and constants for CampaignsListPage
 */

export const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'uploaded', label: 'Uploaded' },
  { value: 'processed', label: 'Processed' },
  { value: 'ready', label: 'Ready' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' }
];

export const REVIEW_STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  reviewed: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800'
};

export const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-800',
  uploaded: 'bg-blue-100 text-blue-800',
  processed: 'bg-yellow-100 text-yellow-800',
  ready: 'bg-green-100 text-green-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800'
};

/**
 * Format a date string to a readable format
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
};

/**
 * Truncate text to a maximum length
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '—';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Calculate time until scheduled date
 */
export const getTimeUntilScheduled = (scheduledAt) => {
  if (!scheduledAt) return null;
  try {
    const scheduled = new Date(scheduledAt);
    const now = new Date();
    const diff = scheduled - now;
    
    if (diff <= 0) return 'Past due';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  } catch {
    return null;
  }
};

