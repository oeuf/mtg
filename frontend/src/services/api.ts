import axios from "axios";
import type {
  Card,
  CardSearchFilters,
  Commander,
  ComboResponse,
  DeckShell,
  DeckAnalysis,
  SimilarCardsResponse,
  CardSynergiesResponse,
  CommanderSynergiesResponse,
  CommanderRecommendationsResponse,
  GraphListResponse,
} from "../types";
import type { AutocompleteItem } from "../components/SearchAutocomplete";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export const commandersAPI = {
  list(page = 1, limit = 20) {
    return api.get<{ items: Commander[]; total: number }>("/api/commanders", {
      params: { page, limit },
    });
  },

  get(name: string) {
    return api.get<Commander>(`/api/commanders/${encodeURIComponent(name)}`);
  },

  getSynergies(name: string, params?: { limit?: number }) {
    return api.get<CommanderSynergiesResponse>(
      `/api/commanders/${encodeURIComponent(name)}/synergies`,
      { params },
    );
  },

  getRecommendations(name: string, params?: { top_k?: number }) {
    return api.get<CommanderRecommendationsResponse>(
      `/api/commanders/${encodeURIComponent(name)}/recommendations`,
      { params },
    );
  },
};

export const cardsAPI = {
  search(filters: CardSearchFilters) {
    return api.get<{ items: Card[]; total: number }>("/api/cards", {
      params: filters,
    });
  },

  get(name: string) {
    return api.get<Card>(`/api/cards/${encodeURIComponent(name)}`);
  },

  getSimilar(name: string, params?: { limit?: number }) {
    return api.get<SimilarCardsResponse>(
      `/api/cards/${encodeURIComponent(name)}/similar`,
      { params },
    );
  },

  getSynergies(name: string) {
    return api.get<CardSynergiesResponse>(
      `/api/cards/${encodeURIComponent(name)}/synergies`,
    );
  },

  getCombos(name: string) {
    return api.get<{ card: string; combos: ComboResponse[] }>(
      `/api/cards/${encodeURIComponent(name)}/combos`,
    );
  },

  getByRole(role: string, colorIdentity?: string[]) {
    return api.get<Card[]>(`/api/cards/by-role/${encodeURIComponent(role)}`, {
      params: colorIdentity ? { color_identity: colorIdentity } : undefined,
    });
  },

  autocomplete(query: string, commanderOnly = false) {
    return api.get<AutocompleteItem[]>("/api/cards/autocomplete", {
      params: { q: query, commander_only: commanderOnly },
    });
  },
};

export const decksAPI = {
  buildShell(commanderName: string) {
    return api.post<DeckShell>("/api/decks/build-shell", {
      commander: commanderName,
    });
  },

  analyze(deck: { commander: string; cards: string[] }) {
    return api.post<DeckAnalysis>("/api/decks/analyze", deck);
  },
};

export const graphAPI = {
  stats() {
    return api.get<Record<string, number>>("/api/graph/stats");
  },

  mechanics() {
    return api.get<GraphListResponse>("/api/mechanics");
  },

  themes() {
    return api.get<GraphListResponse>("/api/themes");
  },

  roles() {
    return api.get<GraphListResponse>("/api/roles");
  },
};

export default api;
