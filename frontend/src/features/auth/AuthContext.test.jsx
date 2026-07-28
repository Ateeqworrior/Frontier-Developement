import { renderHook, act } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuthProvider, useAuth } from "./AuthContext.jsx";

describe("AuthContext", () => {
  it("throws when useAuth is called outside a provider", () => {
    expect(() => renderHook(() => useAuth())).toThrow("useAuth must be used within AuthProvider");
  });

  it("starts with no session, then login/logout update it", () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    expect(result.current.session).toBeNull();

    act(() => {
      result.current.login({ access_token: "tok-1", user_id: 7, role: "user" });
    });
    expect(result.current.session).toEqual({ token: "tok-1", userId: 7, role: "user" });

    act(() => {
      result.current.logout();
    });
    expect(result.current.session).toBeNull();
  });
});
