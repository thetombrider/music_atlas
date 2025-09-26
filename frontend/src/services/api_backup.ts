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

const API_BASE_URL = 'https://music-atlas-1758921214.loca.lt/api/v1';
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
      // Token scaduto, rimuovi dal localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  // Inizia il login Spotify
  async initiateSpotifyLogin(): Promise<SpotifyLoginResponse> {
    const response = await api.get<SpotifyLoginResponse>('/auth/spotify/login');
    return response.data;
  },

  // Gestisce callback OAuth
  async handleSpotifyCallback(code: string, state?: string): Promise<SpotifyAuthResponse> {
    const response = await api.post<SpotifyAuthResponse>('/auth/spotify/callback', {
      code,
      state,
    });
    return response.data;
  },

  // Ottieni info utente corrente
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  // Refresh token
  async refreshToken(): Promise<{ message: string; expires_at: number }> {
    const response = await api.post('/auth/refresh');
    return response.data;
  },

  // Logout
  async logout(): Promise<{ message: string }> {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Music API
export const musicAPI = {
  // Importa dati utente nel knowledge graph
  async importUserData(): Promise<{ message: string; spotify_user_id: string; status: string }> {
    const response = await api.post('/music/import');
    return response.data;
  },

  // Ottieni top artists
  async getTopArtists(timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term', limit = 20): Promise<TopItemsResponse<Artist>> {
    const response = await api.get<TopItemsResponse<Artist>>('/music/top-artists', {
      params: { time_range: timeRange, limit },
    });
    return response.data;
  },

  // Ottieni top tracks
  async getTopTracks(timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term', limit = 20): Promise<TopItemsResponse<Track>> {
    const response = await api.get<TopItemsResponse<Track>>('/music/top-tracks', {
      params: { time_range: timeRange, limit },
    });
    return response.data;
  },

  // Ottieni profilo Spotify
  async getSpotifyProfile(): Promise<{ spotify_profile: any }> {
    const response = await api.get('/music/profile');
    return response.data;
  },

  // Ottieni stato import
  async getImportStatus(): Promise<ImportStatus> {
    const response = await api.get<ImportStatus>('/music/import-status');
    return response.data;
  },
};

// Utility functions
export const authUtils = {
  // Salva token nel localStorage
  saveAuthData(authResponse: SpotifyAuthResponse) {
    localStorage.setItem('access_token', authResponse.access_token);
    localStorage.setItem('user_data', JSON.stringify(authResponse.user_profile));
  },

  // Ottieni token dal localStorage
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  // Ottieni dati utente dal localStorage
  getUserData(): any {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  },

  // Controlla se l'utente è autenticato
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  // Logout completo
  clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  },
};

export default api;
