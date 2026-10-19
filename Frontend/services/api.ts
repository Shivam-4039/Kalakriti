import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

const TOKEN_KEY = 'kalakriti_jwt_token';

// Read raw API URL from environment variables or fallback
const rawUrl =
  process.env.EXPO_PUBLIC_API_URL ||
  Constants.expoConfig?.extra?.apiUrl ||
  'http://10.0.2.2:8000/api/v1';

// Clean trailing slashes and guarantee /api/v1 prefix exists
const cleanUrl = rawUrl.replace(/\/+$/, '');
const BASE_URL = cleanUrl.endsWith('/api/v1') ? cleanUrl : `${cleanUrl}/api/v1`;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30-second timeout for AI processing & media uploads
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Helper utilities for secure token persistence
export const getStoredToken = async (): Promise<string | null> => {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch (error) {
    console.error('[API] Failed to fetch auth token from SecureStore:', error);
    return null;
  }
};

export const setStoredToken = async (token: string): Promise<void> => {
  try {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  } catch (error) {
    console.error('[API] Failed to save auth token to SecureStore:', error);
  }
};

export const removeStoredToken = async (): Promise<void> => {
  try {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch (error) {
    console.error('[API] Failed to delete auth token from SecureStore:', error);
  }
};

// Request Interceptor: Attach bearer token to outgoing requests
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = await getStoredToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('[API] Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor: Normalize API errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as { detail?: string };

      console.error(`[API Error] ${status}:`, data?.detail || 'Unknown server error');

      if (status === 401) {
        // Clear expired token on unauthorized response
        await removeStoredToken();
      }

      return Promise.reject(new Error(data?.detail || `Server error (${status})`));
    } else if (error.request) {
      console.error('[API Error] Network unreachable or timeout:', error.message);
      return Promise.reject(new Error('Network connection failed. Please check internet.'));
    }

    console.error('[API Error] Request execution failed:', error.message);
    return Promise.reject(error);
  }
);