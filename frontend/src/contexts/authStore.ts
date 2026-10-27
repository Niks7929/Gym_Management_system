import { create } from 'zustand';
import type { User } from '../types';

interface AuthStoreState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  updateUser: (user: Partial<User>) => void;
  logout: () => void;
}

// In-Memory Zustand Store - Strictly No localStorage / sessionStorage to prevent XSS exploits
export const useAuthStore = create<AuthStoreState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,
  setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
  updateUser: (updatedFields) => set((state) => ({
    user: state.user ? { ...state.user, ...updatedFields } : null
  })),
  logout: () => set({ token: null, user: null, isAuthenticated: false }),
}));
