import { useCallback } from "react";
import { useAuth } from "../context/AuthContext";

export function useApi() {
  const { token } = useAuth();

  const apiFetch = useCallback(
    async (path: string, init?: RequestInit) => {
      const res = await fetch(path, {
        ...init,
        headers: {
          ...(init?.headers ?? {}),
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      return res.json();
    },
    [token]
  );

  return { apiFetch };
}
