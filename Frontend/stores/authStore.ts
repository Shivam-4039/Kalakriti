import { create } from 'zustand';
import { api, setStoredToken, removeStoredToken, getStoredToken } from '../services/api';

export interface Artisan {
  id: string;
  phone_number: string;
  name?: string;
  language_code: string;
  state?: string;
  craft_type?: string;
  created_at?: string;
}

interface AuthState {
  artisan: Artisan | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isDemoMode: boolean;
  
  // Actions
  sendOtp: (phoneNumber: string) => Promise<boolean>;
  verifyOtp: (phoneNumber: string, otp: string) => Promise<boolean>;
  loadSession: () => Promise<void>;
  updateProfile: (data: Partial<Artisan>) => Promise<boolean>;
  logout: () => Promise<void>;
  enableDemoMode: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  artisan: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  isDemoMode: false,

  // Step 1: Request OTP or trigger demo flow
  sendOtp: async (phoneNumber: string) => {
    try {
      set({ isLoading: true });
      
      // Demo numbers shortcut handling
      if (phoneNumber === '+919999999999' || phoneNumber === '+919876543210') {
        console.log('[Auth] Demo phone detected. Requesting demo OTP.');
      }

      await api.post('/auth/send-otp', { phone_number: phoneNumber });
      return true;
    } catch (error) {
      console.error('[AuthStore] sendOtp error:', error);
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  // Step 2: Verify 6-digit OTP and store JWT
  verifyOtp: async (phoneNumber: string, otp: string) => {
    try {
      set({ isLoading: true });
      const response = await api.post<{ access_token: string; artisan: Artisan }>(
        '/auth/verify-otp',
        { phone_number: phoneNumber, otp }
      );

      const { access_token, artisan } = response.data;

      await setStoredToken(access_token);
      set({
        token: access_token,
        artisan,
        isAuthenticated: true,
        isDemoMode: phoneNumber === '+919999999999' || phoneNumber === '+919876543210',
      });

      return true;
    } catch (error) {
      console.error('[AuthStore] verifyOtp error:', error);
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  // Auto-restore session on app startup
  loadSession: async () => {
    try {
      set({ isLoading: true });
      const token = await getStoredToken();

      if (!token) {
        set({ isAuthenticated: false, artisan: null, token: null, isLoading: false });
        return;
      }

      // Validate token with backend
      const response = await api.get<Artisan>('/auth/me');
      set({
        token,
        artisan: response.data,
        isAuthenticated: true,
      });
    } catch (error) {
      console.error('[AuthStore] Session load failed, clearing token:', error);
      await removeStoredToken();
      set({ token: null, artisan: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },

  // Update artisan profile (name, language, state)
  updateProfile: async (data: Partial<Artisan>) => {
    try {
      set({ isLoading: true });
      const response = await api.put<Artisan>('/auth/me', data);
      set({ artisan: response.data });
      return true;
    } catch (error) {
      console.error('[AuthStore] updateProfile error:', error);
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  // Demo shortcut button action
  enableDemoMode: async () => {
    const demoPhone = '+919999999999';
    const demoOtp = '123456';
    await get().sendOtp(demoPhone);
    await get().verifyOtp(demoPhone, demoOtp);
  },

  // Purge token and clear store state
  logout: async () => {
    await removeStoredToken();
    set({
      artisan: null,
      token: null,
      isAuthenticated: false,
      isDemoMode: false,
    });
  },
}));