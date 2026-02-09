import type { ReactNode } from 'react';

type BadgeVariant = 'default' | 'mana-W' | 'mana-U' | 'mana-B' | 'mana-R' | 'mana-G';

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-700 text-gray-200',
  'mana-W': 'bg-mana-white text-gray-900',
  'mana-U': 'bg-mana-blue text-white',
  'mana-B': 'bg-mana-black text-white',
  'mana-R': 'bg-mana-red text-white',
  'mana-G': 'bg-mana-green text-white',
};

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
