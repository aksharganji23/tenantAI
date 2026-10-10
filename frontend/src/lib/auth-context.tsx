'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, Tenant, DemoAccount } from './types';
import { api, clearStoredToken } from './api';

interface AuthContextType {
  user: User | null;
  tenant: Tenant | null;
  loading: boolean;
  demoAccounts: DemoAccount[];
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  switchDemoAccount: (email: string, password: string) => Promise<void>;
  refreshTenant: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [loading, setLoading] = useState(true);
  const [demoAccounts, setDemoAccounts] = useState<DemoAccount[]>([]);

  // Load demo accounts for 1-click test switchers
  const loadDemoAccounts = useCallback(async () => {
    try {
      const res = await api.demo.getAccounts();
      setDemoAccounts(res.accounts);
    } catch (err) {
      console.warn('Could not load demo accounts:', err);
    }
  }, []);

  // Fetch current user and tenant from token
  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await api.auth.me();
      setUser(currentUser);
      try {
        const currentTenant = await api.tenants.getCurrent();
        setTenant(currentTenant);
      } catch {
        // Superadmin or no tenant
      }
    } catch {
      setUser(null);
      setTenant(null);
      clearStoredToken();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDemoAccounts();
    refreshUser();
  }, [loadDemoAccounts, refreshUser]);

  const login = async (email: string, password: string): Promise<User> => {
    const res = await api.auth.login(email, password);
    setUser(res.user);
    try {
      const t = await api.tenants.getCurrent();
      setTenant(t);
    } catch {
      setTenant(null);
    }
    return res.user;
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch {
      clearStoredToken();
    }
    setUser(null);
    setTenant(null);
  };

  const switchDemoAccount = async (email: string, password: string) => {
    setLoading(true);
    try {
      await login(email, password);
    } finally {
      setLoading(false);
    }
  };

  const refreshTenant = async () => {
    try {
      const t = await api.tenants.getCurrent();
      setTenant(t);
    } catch (e) {
      console.warn('Error refreshing tenant:', e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tenant,
        loading,
        demoAccounts,
        login,
        logout,
        switchDemoAccount,
        refreshTenant,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
