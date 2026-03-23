import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { CardSkeleton, TextSkeleton, GridSkeleton } from '../LoadingSkeleton';

describe('LoadingSkeleton', () => {
  describe('CardSkeleton', () => {
    it('renders with pulse animation', () => {
      const { container } = render(<CardSkeleton />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('animate-pulse');
    });

    it('renders as a div element', () => {
      const { container } = render(<CardSkeleton />);
      expect(container.firstChild?.nodeName).toBe('DIV');
    });
  });

  describe('TextSkeleton', () => {
    it('renders with pulse animation', () => {
      const { container } = render(<TextSkeleton />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('animate-pulse');
    });

    it('accepts custom width class', () => {
      const { container } = render(<TextSkeleton width="w-3/4" />);
      const skeleton = container.firstChild as HTMLElement;
      expect(skeleton.className).toContain('w-3/4');
    });
  });

  describe('GridSkeleton', () => {
    it('renders correct number of skeleton items', () => {
      const { container } = render(<GridSkeleton count={6} />);
      const skeletons = container.querySelectorAll('[data-testid="card-skeleton"]');
      expect(skeletons.length).toBe(6);
    });

    it('defaults to 8 items', () => {
      const { container } = render(<GridSkeleton />);
      const skeletons = container.querySelectorAll('[data-testid="card-skeleton"]');
      expect(skeletons.length).toBe(8);
    });
  });
});
