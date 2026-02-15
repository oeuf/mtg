import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  render,
  screen,
  fireEvent,
  act,
  waitFor,
} from '@testing-library/react';
import { SearchAutocomplete } from '../SearchAutocomplete';
import type { AutocompleteItem } from '../SearchAutocomplete';

const mockSuggestions: AutocompleteItem[] = [
  { name: 'Sol Ring', type_line: 'Artifact', mana_cost: '{1}' },
  {
    name: 'Solemn Simulacrum',
    type_line: 'Artifact Creature',
    mana_cost: '{4}',
  },
  { name: 'Sorcerous Spyglass', type_line: 'Artifact', mana_cost: '{2}' },
];

const mockFetch = vi.fn(() => Promise.resolve(mockSuggestions));
const mockSelect = vi.fn();
const mockChange = vi.fn();

async function typeAndWait(input: HTMLElement, value: string) {
  await act(async () => {
    fireEvent.change(input, { target: { value } });
  });
  // Advance past the debounce timer
  await act(async () => {
    vi.advanceTimersByTime(300);
  });
  // Flush resolved promise microtasks
  await act(async () => {
    await Promise.resolve();
  });
}

describe('SearchAutocomplete', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
    mockFetch.mockResolvedValue(mockSuggestions);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders input with placeholder', () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    expect(screen.getByPlaceholderText('Search...')).toBeTruthy();
  });

  it('renders label when provided', () => {
    render(
      <SearchAutocomplete
        label="Card search"
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    expect(screen.getByText('Card search')).toBeTruthy();
  });

  it('shows dropdown with suggestions after typing and debounce', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await typeAndWait(input, 'Sol');

    expect(screen.getByText('Sol Ring')).toBeTruthy();
  });

  it('does not fetch below minChars threshold', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
        minChars={3}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'So' } });
    });
    await act(async () => {
      vi.advanceTimersByTime(300);
    });

    expect(mockFetch).not.toHaveBeenCalled();
  });

  it('calls onSelect when clicking a suggestion', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await typeAndWait(input, 'Sol');

    expect(screen.getByText('Sol Ring')).toBeTruthy();
    fireEvent.mouseDown(screen.getByText('Sol Ring'));
    expect(mockSelect).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('navigates with keyboard and selects with Enter', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await typeAndWait(input, 'Sol');

    expect(screen.getByText('Sol Ring')).toBeTruthy();
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(mockSelect).toHaveBeenCalledWith(mockSuggestions[0]);
  });

  it('closes dropdown on Escape', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await typeAndWait(input, 'Sol');

    expect(screen.getByText('Sol Ring')).toBeTruthy();
    fireEvent.keyDown(input, { key: 'Escape' });
    expect(screen.queryByText('Sol Ring')).toBeNull();
  });

  it('shows no results message when fetch returns empty', async () => {
    mockFetch.mockResolvedValue([]);
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await typeAndWait(input, 'xyz');

    expect(screen.getByText(/no results/i)).toBeTruthy();
  });

  it('calls onChange when input value changes', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        onChange={mockChange}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    fireEvent.change(input, { target: { value: 'test' } });
    expect(mockChange).toHaveBeenCalledWith('test');
  });

  it('debounces fetch calls', async () => {
    render(
      <SearchAutocomplete
        placeholder="Search..."
        onSelect={mockSelect}
        fetchSuggestions={mockFetch}
      />,
    );
    const input = screen.getByPlaceholderText('Search...');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'S' } });
      fireEvent.change(input, { target: { value: 'So' } });
      fireEvent.change(input, { target: { value: 'Sol' } });
    });
    await act(async () => {
      vi.advanceTimersByTime(300);
    });
    await act(async () => {
      await Promise.resolve();
    });

    // Should only have been called once with the final value
    expect(mockFetch).toHaveBeenCalledTimes(1);
    expect(mockFetch).toHaveBeenCalledWith('Sol');
  });
});
