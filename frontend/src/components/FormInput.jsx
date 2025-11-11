/**
 * Reusable form input component
 */
function FormInput({
  label,
  name,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  maxLength,
  rows,
  ...props
}) {
  const inputId = `input-${name}`;
  const isTextarea = type === 'textarea';

  return (
    <div className="mb-6">
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {isTextarea ? (
        <textarea
          id={inputId}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          maxLength={maxLength}
          rows={rows || 4}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          {...props}
        />
      ) : (
        <input
          id={inputId}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          maxLength={maxLength}
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          {...props}
        />
      )}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      {maxLength && (
        <p className="mt-1 text-xs text-gray-500">
          {value?.length || 0} / {maxLength} characters
        </p>
      )}
    </div>
  );
}

export default FormInput;

