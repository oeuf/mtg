import type React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ErrorBoundary } from '../ErrorBoundary';
import { LoadingSpinner } from '../LoadingSpinner';

function ThrowingComponent(): React.ReactNode {
  throw new Error('Test error');
}

describe('ErrorBoundary', () => {
  it('renders children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <p>Safe content</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText('Safe content')).toBeInTheDocument();
  });

  it('shows default fallback when child throws', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>,
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Try Again' })).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it('shows custom fallback when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    render(
      <ErrorBoundary fallback={<p>Custom error</p>}>
        <ThrowingComponent />
      </ErrorBoundary>,
    );
    expect(screen.getByText('Custom error')).toBeInTheDocument();
    vi.restoreAllMocks();
  });
});

describe('LoadingSpinner', () => {
  it('renders with default medium size', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');
    expect(spinner.className).toContain('h-8');
    expect(spinner.className).toContain('w-8');
  });

  it('renders with small size', () => {
    render(<LoadingSpinner size="sm" />);
    const spinner = screen.getByRole('status');
    expect(spinner.className).toContain('h-4');
    expect(spinner.className).toContain('w-4');
  });

  it('renders with large size', () => {
    render(<LoadingSpinner size="lg" />);
    const spinner = screen.getByRole('status');
    expect(spinner.className).toContain('h-12');
    expect(spinner.className).toContain('w-12');
  });

  it('applies custom className', () => {
    const { container } = render(<LoadingSpinner className="mt-4" />);
    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.className).toContain('mt-4');
  });
});
