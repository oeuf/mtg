interface ToastProps {
  id: string;
  message: string;
  variant: 'success' | 'error' | 'info';
  onDismiss: (id: string) => void;
}

const variantStyles = {
  success: 'bg-green-800 border-green-600 text-green-100',
  error: 'bg-red-800 border-red-600 text-red-100',
  info: 'bg-blue-800 border-blue-600 text-blue-100',
};

export function Toast({ id, message, variant, onDismiss }: ToastProps) {
  return (
    <div className={`${variantStyles[variant]} border rounded-lg px-4 py-3 shadow-lg flex items-center justify-between gap-2`}>
      <span>{message}</span>
      <button
        onClick={() => onDismiss(id)}
        className="text-current opacity-70 hover:opacity-100"
        aria-label="Dismiss"
      >
        ✕
      </button>
    </div>
  );
}
