/**
 * Schedule Modal Component - For scheduling campaigns
 */
function ScheduleModal({ 
  show, 
  campaign, 
  scheduleDateTime, 
  onDateTimeChange, 
  onSubmit, 
  onCancel, 
  isScheduling 
}) {
  if (!show || !campaign) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          Schedule Campaign
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Schedule "{campaign.campaign_name}" for future sending.
        </p>
        
        <div className="mb-4">
          <label htmlFor="schedule-datetime" className="block text-sm font-medium text-gray-700 mb-2">
            Date & Time
          </label>
          <input
            type="datetime-local"
            id="schedule-datetime"
            value={scheduleDateTime}
            onChange={(e) => onDateTimeChange(e.target.value)}
            min={new Date().toISOString().slice(0, 16)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Select a future date and time
          </p>
        </div>

        <div className="flex items-center justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={onSubmit}
            disabled={!scheduleDateTime || isScheduling}
            className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScheduling ? 'Scheduling...' : 'Schedule'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ScheduleModal;

