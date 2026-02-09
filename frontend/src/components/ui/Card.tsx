import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  header?: string;
}

export function Card({ children, className = '', header }: CardProps) {
  return (
    <div className={`bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {header && (
        <div className="px-4 py-3 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">{header}</h3>
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
