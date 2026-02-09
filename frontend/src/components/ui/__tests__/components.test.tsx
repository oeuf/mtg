import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button, Card, Input, Badge } from '..';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('handles click events', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('applies primary variant classes by default', () => {
    render(<Button>Primary</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-brand-600');
  });

  it('applies secondary variant classes', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-gray-700');
  });

  it('applies ghost variant classes', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-transparent');
  });

  it('applies size classes', () => {
    render(<Button size="lg">Large</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('px-6');
    expect(btn.className).toContain('text-lg');
  });

  it('supports disabled state', () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders header when provided', () => {
    render(<Card header="My Header">Content</Card>);
    expect(screen.getByText('My Header')).toBeInTheDocument();
  });

  it('does not render header element when not provided', () => {
    const { container } = render(<Card>Content</Card>);
    expect(container.querySelector('h3')).toBeNull();
  });
});

describe('Input', () => {
  it('renders label', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<Input label="Email" error="Required field" />);
    expect(screen.getByText('Required field')).toBeInTheDocument();
  });

  it('applies error border class when error is present', () => {
    render(<Input label="Email" error="Bad" />);
    const input = screen.getByLabelText('Email');
    expect(input.className).toContain('border-red-500');
  });

  it('does not show error when not provided', () => {
    const { container } = render(<Input label="Name" />);
    expect(container.querySelector('.text-red-500')).toBeNull();
  });
});

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Default</Badge>);
    expect(screen.getByText('Default')).toBeInTheDocument();
  });

  it('applies default variant classes', () => {
    render(<Badge>Tag</Badge>);
    expect(screen.getByText('Tag').className).toContain('bg-gray-700');
  });

  it('applies mana-U variant classes', () => {
    render(<Badge variant="mana-U">Blue</Badge>);
    expect(screen.getByText('Blue').className).toContain('bg-mana-blue');
  });

  it('applies mana-G variant classes', () => {
    render(<Badge variant="mana-G">Green</Badge>);
    expect(screen.getByText('Green').className).toContain('bg-mana-green');
  });
});
