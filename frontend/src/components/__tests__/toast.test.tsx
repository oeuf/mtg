import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { Toast } from '../Toast';
import { ToastProvider, useToast } from '../ToastContext';

describe('Toast', () => {
  it('renders message text', () => {
    render(<Toast id="1" message="Test message" variant="success" onDismiss={() => {}} />);
    expect(screen.getByText('Test message')).toBeTruthy();
  });

  it('renders success variant with green styling', () => {
    const { container } = render(<Toast id="1" message="Success" variant="success" onDismiss={() => {}} />);
    const toast = container.firstChild as HTMLElement;
    expect(toast.className).toContain('green');
  });

  it('renders error variant with red styling', () => {
    const { container } = render(<Toast id="1" message="Error" variant="error" onDismiss={() => {}} />);
    const toast = container.firstChild as HTMLElement;
    expect(toast.className).toContain('red');
  });

  it('renders info variant with blue styling', () => {
    const { container } = render(<Toast id="1" message="Info" variant="info" onDismiss={() => {}} />);
    const toast = container.firstChild as HTMLElement;
    expect(toast.className).toContain('blue');
  });
});

describe('ToastContext', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  function TestComponent() {
    const { addToast } = useToast();
    return (
      <button onClick={() => addToast('Hello!', 'success')}>
        Add Toast
      </button>
    );
  }

  it('adds toast via useToast hook', async () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    );

    await act(async () => {
      screen.getByText('Add Toast').click();
    });

    expect(screen.getByText('Hello!')).toBeTruthy();
  });

  it('auto-dismisses toast after timeout', async () => {
    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    );

    await act(async () => {
      screen.getByText('Add Toast').click();
    });

    expect(screen.getByText('Hello!')).toBeTruthy();

    await act(async () => {
      vi.advanceTimersByTime(4000);
    });

    expect(screen.queryByText('Hello!')).toBeNull();
  });
});
