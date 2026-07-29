import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { authClient } from "./authClient.js";

function mockFetchOnce(status, body) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
}

describe("authClient", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns response data on success", async () => {
    mockFetchOnce(200, { success: true, data: { id: 1 } });
    const data = await authClient.me("tok");
    expect(data).toEqual({ id: 1 });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/me"),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer tok" }) })
    );
  });

  it("throws an error carrying status/code/body on failure", async () => {
    mockFetchOnce(409, { message: "dup", message_code: "duplicate_resource", error: { detail: "exists" } });
    await expect(authClient.register({ email: "a@b.com" })).rejects.toMatchObject({
      status: 409,
      code: "duplicate_resource",
    });
  });

  it("encodes the CARS callback code in the query string", async () => {
    mockFetchOnce(200, { success: true, data: { access_token: "t" } });
    await authClient.exchangeCarsCode("dev-code:a@b.com:pw:true");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining(encodeURIComponent("dev-code:a@b.com:pw:true")),
      expect.anything()
    );
  });
});
