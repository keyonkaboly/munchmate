import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import api from '../api';
import { CUSTOMER_STORAGE_KEY, writeStoredCustomerId } from '../customerSession';

interface AuthUser {
  id: number;
  email: string;
  username: string;
  user_type: 'customer' | 'restaurant_manager';
  restaurant_manager_restaurant_id: number | null;
}

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  role: 'customer' | 'restaurant_manager';
}

interface LoginPayload {
  email: string;
  password: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  refreshUser: () => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const response = await api.get<AuthUser>('/auth/me');
      setUser(response.data);
      writeStoredCustomerId(response.data.id);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setLoading(true);
      await refreshUser();
      if (!cancelled) setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshUser]);

  const register = useCallback(async (payload: RegisterPayload) => {
    const res = await api.post<{ id?: number }>(`/auth/register?role=${payload.role}`, {
      username: payload.username,
      email: payload.email,
      password: payload.password,
    });
    if (res.data?.id != null) {
      writeStoredCustomerId(res.data.id);
    }
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    await api.post('/auth/login', payload);
    await refreshUser();
  }, [refreshUser]);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      setUser(null);
      sessionStorage.removeItem(CUSTOMER_STORAGE_KEY);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: user !== null,
      refreshUser,
      register,
      login,
      logout,
    }),
    [user, loading, refreshUser, register, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
