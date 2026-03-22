import { describe, it, expect, vi, beforeEach } from "vitest";
import axios from "axios";
import { commandersAPI, cardsAPI, graphAPI } from "../api";

vi.mock("axios", () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
  };
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      ...mockAxiosInstance,
    },
  };
});

function getMockApi() {
  return axios.create() as unknown as {
    get: ReturnType<typeof vi.fn>;
    post: ReturnType<typeof vi.fn>;
  };
}

beforeEach(() => {
  const mock = getMockApi();
  mock.get.mockReset();
  mock.post.mockReset();
});

describe("commandersAPI", () => {
  it("list calls /api/commanders with pagination params", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await commandersAPI.list(2, 10);

    expect(mock.get).toHaveBeenCalledWith("/api/commanders", {
      params: { page: 2, limit: 10 },
    });
  });

  it("list uses default pagination", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await commandersAPI.list();

    expect(mock.get).toHaveBeenCalledWith("/api/commanders", {
      params: { page: 1, limit: 20 },
    });
  });

  it("list passes search param when provided", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await commandersAPI.list(1, 50, "muldrotha");

    expect(mock.get).toHaveBeenCalledWith("/api/commanders", {
      params: { page: 1, limit: 50, search: "muldrotha" },
    });
  });

  it("list omits search param when not provided", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await commandersAPI.list(1, 50);

    expect(mock.get).toHaveBeenCalledWith("/api/commanders", {
      params: { page: 1, limit: 50 },
    });
  });

  it("get calls /api/commanders/{name} with encoded name", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: {} });

    await commandersAPI.get("Muldrotha, the Gravetide");

    expect(mock.get).toHaveBeenCalledWith(
      "/api/commanders/Muldrotha%2C%20the%20Gravetide",
    );
  });

  it("getSynergies passes limit param", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await commandersAPI.getSynergies("Muldrotha, the Gravetide", {
      limit: 5,
    });

    expect(mock.get).toHaveBeenCalledWith(
      "/api/commanders/Muldrotha%2C%20the%20Gravetide/synergies",
      { params: { limit: 5 } },
    );
  });

  it("getRecommendations passes top_k param", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await commandersAPI.getRecommendations("Muldrotha, the Gravetide", {
      top_k: 10,
    });

    expect(mock.get).toHaveBeenCalledWith(
      "/api/commanders/Muldrotha%2C%20the%20Gravetide/recommendations",
      { params: { top_k: 10 } },
    );
  });
});

describe("cardsAPI", () => {
  it("search passes filters as params", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    const filters = { page: 1, limit: 20, text_search: "draw" };
    await cardsAPI.search(filters);

    expect(mock.get).toHaveBeenCalledWith("/api/cards", {
      params: filters,
    });
  });

  it("get calls /api/cards/{name} with encoded name", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: {} });

    await cardsAPI.get("Eternal Witness");

    expect(mock.get).toHaveBeenCalledWith(
      "/api/cards/Eternal%20Witness",
    );
  });

  it("getSimilar passes limit param", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await cardsAPI.getSimilar("Necropotence", { limit: 10 });

    expect(mock.get).toHaveBeenCalledWith(
      "/api/cards/Necropotence/similar",
      { params: { limit: 10 } },
    );
  });

  it("getSynergies calls correct URL", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await cardsAPI.getSynergies("Sol Ring");

    expect(mock.get).toHaveBeenCalledWith(
      "/api/cards/Sol%20Ring/synergies",
    );
  });

  it("getByRole passes color_identity params", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await cardsAPI.getByRole("ramp", ["G"]);

    expect(mock.get).toHaveBeenCalledWith("/api/cards/by-role/ramp", {
      params: { color_identity: ["G"] },
    });
  });

  it("getByRole omits params when no color identity", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await cardsAPI.getByRole("draw");

    expect(mock.get).toHaveBeenCalledWith("/api/cards/by-role/draw", {
      params: undefined,
    });
  });
});


describe("graphAPI", () => {
  it("stats calls /api/graph/stats", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: {} });

    await graphAPI.stats();

    expect(mock.get).toHaveBeenCalledWith("/api/graph/stats");
  });

  it("mechanics calls /api/mechanics", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await graphAPI.mechanics();

    expect(mock.get).toHaveBeenCalledWith("/api/mechanics");
  });

  it("themes calls /api/themes", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await graphAPI.themes();

    expect(mock.get).toHaveBeenCalledWith("/api/themes");
  });

  it("roles calls /api/roles", async () => {
    const mock = getMockApi();
    mock.get.mockResolvedValueOnce({ data: [] });

    await graphAPI.roles();

    expect(mock.get).toHaveBeenCalledWith("/api/roles");
  });
});
