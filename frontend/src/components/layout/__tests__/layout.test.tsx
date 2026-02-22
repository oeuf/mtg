import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { Header, Layout } from '..';

function renderInRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('Header', () => {
  it('renders app title', () => {
    renderInRouter(<Header />);
    expect(screen.getByText('MTG Commander')).toBeInTheDocument();
  });

  it('renders all navigation links', () => {
    renderInRouter(<Header />);
    expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Commanders' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Cards' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Collection' })).toBeInTheDocument();
  });

  it('links point to correct routes', () => {
    renderInRouter(<Header />);
    expect(screen.getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: 'Commanders' })).toHaveAttribute('href', '/commanders');
    expect(screen.getByRole('link', { name: 'Cards' })).toHaveAttribute('href', '/cards');
    expect(screen.getByRole('link', { name: 'Collection' })).toHaveAttribute('href', '/collection');
  });
});

describe('Layout', () => {
  it('renders children', () => {
    renderInRouter(<Layout><p>Test content</p></Layout>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders header within layout', () => {
    renderInRouter(<Layout><p>Content</p></Layout>);
    expect(screen.getByText('MTG Commander')).toBeInTheDocument();
  });
});
