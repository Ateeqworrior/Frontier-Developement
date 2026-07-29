import { afterEach, describe, expect, it, vi } from "vitest";
import { catalogClient } from "./catalogClient.js";

function mockFetchOnce(status, body) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

describe("catalogClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("listProducts omits empty/undefined filter values from the query string", async () => {
    mockFetchOnce(200, { success: true, data: [], pagination: { page: 1, page_size: 20, total: 0 } });
    await catalogClient.listProducts({ category_id: "", price_min: 10, sort: "recency" });
    const calledUrl = global.fetch.mock.calls[0][0];
    expect(calledUrl).toContain("price_min=10");
    expect(calledUrl).toContain("sort=recency");
    expect(calledUrl).not.toContain("category_id");
  });

  it("listProducts sends no Authorization header when no token is passed", async () => {
    mockFetchOnce(200, { success: true, data: [] });
    await catalogClient.listProducts({});
    expect(global.fetch.mock.calls[0][1].headers).toEqual({});
  });

  it("searchProducts includes q alongside filters", async () => {
    mockFetchOnce(200, { success: true, data: [] });
    await catalogClient.searchProducts("wheelchair", { brand_id: 3 }, "tok");
    const calledUrl = global.fetch.mock.calls[0][0];
    expect(calledUrl).toContain("/products/search");
    expect(calledUrl).toContain("q=wheelchair");
    expect(calledUrl).toContain("brand_id=3");
    expect(global.fetch.mock.calls[0][1].headers).toEqual({ Authorization: "Bearer tok" });
  });

  it("getProductDetail includes pin_code when provided", async () => {
    mockFetchOnce(200, { success: true, data: { id: 1 } });
    await catalogClient.getProductDetail(1, "560001");
    expect(global.fetch.mock.calls[0][0]).toContain("pin_code=560001");
  });

  it("getProductDetail omits pin_code when not provided", async () => {
    mockFetchOnce(200, { success: true, data: { id: 1 } });
    await catalogClient.getProductDetail(1);
    expect(global.fetch.mock.calls[0][0]).not.toContain("pin_code");
  });

  it("throws an error carrying status/code/body on failure", async () => {
    mockFetchOnce(404, { message: "not found", message_code: "product_not_found" });
    await expect(catalogClient.getProductDetail(999)).rejects.toMatchObject({
      status: 404,
      code: "product_not_found",
    });
  });
});
