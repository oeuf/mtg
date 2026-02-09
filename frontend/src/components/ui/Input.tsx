import { forwardRef, type InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...rest }, ref) => {
    const inputId = id || label.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={inputId} className="text-sm font-medium text-gray-300">
          {label}
        </label>
        <input
          ref={ref}
          id={inputId}
          className={`rounded-md border bg-gray-800 px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 ${
            error ? 'border-red-500' : 'border-gray-600'
          } ${className}`}
          {...rest}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>
    );
  },
);

Input.displayName = 'Input';
