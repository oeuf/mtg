import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { CheckboxGroup } from '../CheckboxGroup';
import { RangeSlider } from '../RangeSlider';
import { FilterPanel } from '../FilterPanel';
import type { CardSearchFilters } from '../../../types';

describe('CheckboxGroup', () => {
  const defaultProps = {
    label: 'Card Type',
    options: ['Creature', 'Instant', 'Sorcery'],
    selected: [] as string[],
    onChange: vi.fn(),
  };

  it('renders label and all options', () => {
    render(<CheckboxGroup {...defaultProps} />);
    expect(screen.getByText('Card Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Creature')).toBeInTheDocument();
    expect(screen.getByLabelText('Instant')).toBeInTheDocument();
    expect(screen.getByLabelText('Sorcery')).toBeInTheDocument();
  });

  it('toggles selection on click', () => {
    const onChange = vi.fn();
    render(<CheckboxGroup {...defaultProps} onChange={onChange} />);
    fireEvent.click(screen.getByLabelText('Creature'));
    expect(onChange).toHaveBeenCalledWith(['Creature']);
  });

  it('removes item when clicking selected checkbox', () => {
    const onChange = vi.fn();
    render(
      <CheckboxGroup
        {...defaultProps}
        selected={['Creature', 'Instant']}
        onChange={onChange}
      />,
    );
    fireEvent.click(screen.getByLabelText('Creature'));
    expect(onChange).toHaveBeenCalledWith(['Instant']);
  });
});

describe('RangeSlider', () => {
  const defaultProps = {
    label: 'CMC',
    min: 0,
    max: 16,
    value: [0, 16] as [number, number],
    onChange: vi.fn(),
  };

  it('renders label and min/max inputs', () => {
    render(<RangeSlider {...defaultProps} />);
    expect(screen.getByText('CMC')).toBeInTheDocument();
    const inputs = screen.getAllByRole('spinbutton');
    expect(inputs).toHaveLength(2);
    expect(inputs[0]).toHaveValue(0);
    expect(inputs[1]).toHaveValue(16);
  });

  it('calls onChange when min value changes', () => {
    const onChange = vi.fn();
    render(<RangeSlider {...defaultProps} onChange={onChange} />);
    const inputs = screen.getAllByRole('spinbutton');
    fireEvent.change(inputs[0], { target: { value: '3' } });
    expect(onChange).toHaveBeenCalledWith([3, 16]);
  });

  it('calls onChange when max value changes', () => {
    const onChange = vi.fn();
    render(<RangeSlider {...defaultProps} onChange={onChange} />);
    const inputs = screen.getAllByRole('spinbutton');
    fireEvent.change(inputs[1], { target: { value: '10' } });
    expect(onChange).toHaveBeenCalledWith([0, 10]);
  });
});

describe('FilterPanel', () => {
  const defaultProps = {
    filters: { page: 1, limit: 20 } as CardSearchFilters,
    onUpdateFilter: vi.fn(),
    onClear: vi.fn(),
  };

  it('renders all filter sections', () => {
    render(<FilterPanel {...defaultProps} />);
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Card Type')).toBeInTheDocument();
    expect(screen.getByText('Color')).toBeInTheDocument();
    expect(screen.getByText('CMC')).toBeInTheDocument();
    expect(screen.getByText('Rarity')).toBeInTheDocument();
    expect(screen.getByText('Roles')).toBeInTheDocument();
  });

  it('clear button calls onClear', () => {
    const onClear = vi.fn();
    render(<FilterPanel {...defaultProps} onClear={onClear} />);
    fireEvent.click(screen.getByRole('button', { name: /clear all filters/i }));
    expect(onClear).toHaveBeenCalledOnce();
  });

  it('color buttons toggle selection', () => {
    const onUpdateFilter = vi.fn();
    render(<FilterPanel {...defaultProps} onUpdateFilter={onUpdateFilter} />);
    fireEvent.click(screen.getByRole('button', { name: 'U' }));
    expect(onUpdateFilter).toHaveBeenCalledWith('colors', ['U']);
  });

  it('renders color buttons for all five colors', () => {
    render(<FilterPanel {...defaultProps} />);
    for (const color of ['W', 'U', 'B', 'R', 'G']) {
      expect(screen.getByRole('button', { name: color })).toBeInTheDocument();
    }
  });

  it('shows selected colors with active styling', () => {
    render(
      <FilterPanel
        {...defaultProps}
        filters={{ colors: ['W', 'G'], page: 1, limit: 20 }}
      />,
    );
    const wButton = screen.getByRole('button', { name: 'W' });
    expect(wButton.className).toContain('ring-2');
  });
});
