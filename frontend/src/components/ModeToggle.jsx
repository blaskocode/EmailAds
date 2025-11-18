/**
 * Mode Toggle - Switch between Manual and AI Mode
 */
function ModeToggle({ aiMode, onToggle }) {
  return (
    <div className="flex items-center space-x-3">
      <span className={`text-sm font-medium ${!aiMode ? 'text-hibid-gray-700' : 'text-hibid-gray-500'}`}>
        Manual
      </span>
      <button
        type="button"
        onClick={onToggle}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-hibid-blue-500 focus:ring-offset-2 ${
          aiMode ? 'bg-gradient-hibid' : 'bg-hibid-gray-300'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            aiMode ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      <span className={`text-sm font-medium ${aiMode ? 'text-hibid-gray-700' : 'text-hibid-gray-500'}`}>
        AI Mode
      </span>
    </div>
  );
}

export default ModeToggle;

