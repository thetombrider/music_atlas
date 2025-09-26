import axios from 'axios';
import type { 
  SpotifyLoginResponse, 
  SpotifyAuthResponse, 
  User,
  TopItemsResponse,
  Artist,
  Track,
  ImportStatus,
  ApiResponse
} from '../types/api';

const API_BASE_URL = 'http://localhost:8002/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  },
});

// Request interceptor per aggiungere il token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor per gestire errori
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token scaduto, rimuovi e reindirizza al login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  initiateSpotifyLogin: async (): Promise<SpotifyLoginResponse> => {
    const response = await api.get('/auth/spotify/login');
    return response.data;
  },

  handleSpotifyCallback: async (code: string, state?: string): Promise<SpotifyAuthResponse> => {
    const response = await api.post('/auth/spotify/callback', {
      code,
      state,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<void> => {
    await api.post('/auth/refresh');
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },
};

// Music API endpoints
export const musicAPI = {
  importUserData: async (): Promise<ApiResponse<any>> => {
    const response = await api.post('/music/import');
    return response.data;
  },

  getImportStatus: async (): Promise<ImportStatus> => {
    const response = await api.get('/music/import-status');
    return response.data;
  },

  getTopArtists: async (timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term'): Promise<TopItemsResponse<Artist>> => {
    const response = await api.get(`/music/top-artists?time_range=${timeRange}`);
    return response.data;
  },

  getTopTracks: async (timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term'): Promise<TopItemsResponse<Track>> => {
    const response = await api.get(`/music/top-tracks?time_range=${timeRange}`);
    return response.data;
  },
};

// Auth utilities
export const authUtils = {
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },

  saveAuthData: (authResponse: SpotifyAuthResponse): void => {
    localStorage.setItem('access_token', authResponse.access_token);
    // Note: SpotifyAuthResponse doesn't include refresh_token for now
  },

  clearAuthData: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },
};

export default api;
