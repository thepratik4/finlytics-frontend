import { create } from 'zustand';
import { User } from '../types';

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: JSON.parse(localStorage.getItem('finlytics_user') || 'null'),
  token: localStorage.getItem('finlytics_token'),
  isAuthenticated: !!localStorage.getItem('finlytics_token'),

  setAuth: (user, token) => {
    localStorage.setItem('finlytics_user', JSON.stringify(user));
    localStorage.setItem('finlytics_token', token);
    set({ user, token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('finlytics_user');
    localStorage.removeItem('finlytics_token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));