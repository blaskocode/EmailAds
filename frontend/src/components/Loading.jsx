/**
 * Loading spinner component - Modern design with HiBid branding
 */
function Loading({ message = 'Loading...', size = 'md' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div
        className={`${sizeClasses[size]} border-hibid-gray-200 border-t-hibid-blue-600 rounded-full animate-spin`}
      ></div>
      {message && (
        <p className="mt-4 text-hibid-gray-600 text-sm font-medium">{message}</p>
      )}
    </div>
  );
}

export default Loading;

