import { useState, useEffect } from 'react';
import { authAPI, authUtils, musicAPI } from '../services/api';
import type { User, SpotifyAuthResponse, ImportStatus } from '../types/api';

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    loading: true,
    error: null,
  });

  // Controlla lo stato di autenticazione al mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (!authUtils.isAuthenticated()) {
        setState(prev => ({ ...prev, loading: false }));
        return;
      }

      // Verifica che il token sia ancora valido
      const user = await authAPI.getCurrentUser();
      setState({
        isAuthenticated: true,
        user,
        loading: false,
        error: null,
      });
    } catch (error) {
      console.error('Auth check failed:', error);
      authUtils.clearAuthData();
      setState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: 'Authentication failed',
      });
    }
  };

  const login = async (): Promise<string> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const { authorization_url } = await authAPI.initiateSpotifyLogin();
      
      // Reindirizza a Spotify per l'autorizzazione
      window.location.href = authorization_url;
      
      return authorization_url;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const handleCallback = async (code: string, state?: string): Promise<SpotifyAuthResponse> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const authResponse = await authAPI.handleSpotifyCallback(code, state);
      
      // Salva i dati di autenticazione
      authUtils.saveAuthData(authResponse);
      
      // Aggiorna lo stato locale
      const user: User = {
        id: authResponse.user_profile.id,
        spotify_user_id: authResponse.spotify_user_id,
        display_name: authResponse.user_profile.display_name,
        email: authResponse.user_profile.email,
        images: authResponse.user_profile.images,
        followers: authResponse.user_profile.followers,
        user_profile: authResponse.user_profile,
      };
      
      setState({
        isAuthenticated: true,
        user,
        loading: false,
        error: null,
      });

      return authResponse;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Callback handling failed';
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout API call failed:', error);
    } finally {
      authUtils.clearAuthData();
      setState({
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null,
      });
    }
  };

  const refreshToken = async () => {
    try {
      await authAPI.refreshToken();
      // Il token viene aggiornato automaticamente dal backend
      await checkAuthStatus(); // Ricarica i dati utente
    } catch (error) {
      console.error('Token refresh failed:', error);
      await logout();
    }
  };

  return {
    ...state,
    login,
    logout,
    handleCallback,
    refreshToken,
    checkAuthStatus,
  };
};

// Hook per i dati musicali
export const useMusic = () => {
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startImport = async () => {
    try {
      setImporting(true);
      setError(null);
      
      const result = await musicAPI.importUserData();
      console.log('Import started:', result);
      
      // Polling per controllare lo stato
      pollImportStatus();
      
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Import failed';
      setError(errorMessage);
      throw error;
    } finally {
      setImporting(false);
    }
  };

  const getImportStatus = async () => {
    try {
      const status = await musicAPI.getImportStatus();
      setImportStatus(status);
      return status;
    } catch (error: any) {
      console.error('Failed to get import status:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to get import status';
      setError(errorMessage);
      throw error;
    }
  };

  const pollImportStatus = () => {
    const interval = setInterval(async () => {
      try {
        const status = await getImportStatus();
        if (status?.user_exists && status?.statistics) {
          clearInterval(interval);
        }
      } catch (error) {
        clearInterval(interval);
      }
    }, 2000); // Check ogni 2 secondi

    // Stop polling dopo 30 secondi
    setTimeout(() => clearInterval(interval), 30000);
  };

  const getTopArtists = async (timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term') => {
    try {
      return await musicAPI.getTopArtists(timeRange);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to get top artists';
      setError(errorMessage);
      throw error;
    }
  };

  const getTopTracks = async (timeRange: 'short_term' | 'medium_term' | 'long_term' = 'medium_term') => {
    try {
      return await musicAPI.getTopTracks(timeRange);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to get top tracks';
      setError(errorMessage);
      throw error;
    }
  };

  return {
    importStatus,
    importing,
    error,
    startImport,
    getImportStatus,
    getTopArtists,
    getTopTracks,
  };
};
