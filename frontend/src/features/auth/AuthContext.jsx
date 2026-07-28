import React, { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null); // { token, userId, role }

  const login = (data) => setSession({ token: data.access_token, userId: data.user_id, role: data.role });
  const logout = () => setSession(null);

  return <AuthContext.Provider value={{ session, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
