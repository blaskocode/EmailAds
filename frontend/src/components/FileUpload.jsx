/**
 * File upload component with drag-and-drop support
 */
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];

function FileUpload({
  label,
  files,
  onFilesChange,
  maxFiles = 1,
  required = false,
  error,
  accept = {
    'image/*': ['.png', '.jpg', '.jpeg', '.gif']
  }
}) {
  const [dragActive, setDragActive] = useState(false);

  const validateFile = (file) => {
    if (file.size > MAX_FILE_SIZE) {
      return `File ${file.name} exceeds 5MB limit`;
    }
    if (!ALLOWED_TYPES.includes(file.type)) {
      return `File ${file.name} is not a valid image type`;
    }
    return null;
  };

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const errors = rejectedFiles.map(({ file, errors }) => {
        if (errors.some(e => e.code === 'file-too-large')) {
          return `File ${file.name} exceeds 5MB limit`;
        }
        if (errors.some(e => e.code === 'file-invalid-type')) {
          return `File ${file.name} is not a valid image type`;
        }
        return `File ${file.name} was rejected`;
      });
      // You might want to show these errors to the user
      console.error('Rejected files:', errors);
    }

    // Validate accepted files
    const validFiles = [];
    const fileErrors = [];

    acceptedFiles.forEach(file => {
      const error = validateFile(file);
      if (error) {
        fileErrors.push(error);
      } else {
        validFiles.push(file);
      }
    });

    if (fileErrors.length > 0) {
      // Handle validation errors
      console.error('Validation errors:', fileErrors);
    }

    // Update files based on maxFiles
    if (maxFiles === 1) {
      onFilesChange(validFiles.slice(0, 1));
    } else {
      const currentFiles = files || [];
      const newFiles = [...currentFiles, ...validFiles].slice(0, maxFiles);
      onFilesChange(newFiles);
    }
  }, [files, maxFiles, onFilesChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize: MAX_FILE_SIZE,
    multiple: maxFiles > 1,
    maxFiles: maxFiles
  });

  const removeFile = (indexToRemove) => {
    if (maxFiles === 1) {
      onFilesChange([]);
    } else {
      const newFiles = files.filter((_, index) => index !== indexToRemove);
      onFilesChange(newFiles);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-hibid-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-hibid-blue-500 bg-hibid-blue-50 shadow-hibid'
            : error
            ? 'border-red-500 bg-red-50'
            : 'border-hibid-gray-300 hover:border-hibid-blue-400 hover:bg-hibid-gray-50 bg-hibid-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <svg
            className={`mx-auto h-12 w-12 transition-colors ${
              isDragActive ? 'text-hibid-blue-600' : 'text-hibid-gray-400'
            }`}
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className={`text-sm font-medium ${
            isDragActive ? 'text-hibid-blue-700' : 'text-hibid-gray-600'
          }`}>
            {isDragActive
              ? 'Drop the files here...'
              : 'Drag and drop files here, or click to select'}
          </p>
          <p className="text-xs text-hibid-gray-500">
            {maxFiles === 1
              ? 'PNG, JPG, JPEG, GIF up to 5MB'
              : `Up to ${maxFiles} files, PNG, JPG, JPEG, GIF up to 5MB each`}
          </p>
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-600 font-medium">{error}</p>
      )}

      {/* File previews */}
      {files && files.length > 0 && (
        <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
          {files.map((file, index) => (
            <div
              key={index}
              className="relative border border-hibid-gray-200 rounded-xl overflow-hidden bg-white shadow-hibid hover:shadow-hibid-lg transition-shadow"
            >
              <img
                src={URL.createObjectURL(file)}
                alt={file.name}
                className="w-full h-32 object-cover"
              />
              <div className="p-2">
                <p className="text-xs text-hibid-gray-700 truncate font-medium" title={file.name}>
                  {file.name}
                </p>
                <p className="text-xs text-hibid-gray-500">
                  {formatFileSize(file.size)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1.5 hover:bg-red-600 transition-colors shadow-md hover:shadow-lg"
                aria-label="Remove file"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FileUpload;

