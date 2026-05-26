'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

import { STORAGE_KEYS } from '@/lib/constants';
import type { AuthResponse, User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (payload: AuthResponse) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: ({ user, tokens }) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem(STORAGE_KEYS.accessToken, tokens.access_token);
          localStorage.setItem(STORAGE_KEYS.refreshToken, tokens.refresh_token);
        }
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        });
      },
      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem(STORAGE_KEYS.accessToken);
          localStorage.removeItem(STORAGE_KEYS.refreshToken);
        }
        set({ user: null, accessToken: null, refreshToken: null });
      },
      isAuthenticated: () => !!get().accessToken && !!get().user,
    }),
    { name: 'transcribeop-auth' },
  ),
);
