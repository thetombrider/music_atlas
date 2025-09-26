import React, { useEffect, useState } from 'react';
import { useAuth, useMusic } from '../hooks/useAuth';
import type { Artist, Track, TopItemsResponse } from '../types/api';

const Dashboard: React.FC = () => {
  const { user, logout, loading: authLoading } = useAuth();
  const { 
    importStatus, 
    importing, 
    error: musicError, 
    startImport, 
    getImportStatus,
    getTopArtists,
    getTopTracks 
  } = useMusic();

  const [topArtists, setTopArtists] = useState<Artist[]>([]);
  const [topTracks, setTopTracks] = useState<Track[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'artists' | 'tracks'>('overview');
  const [dataLoaded, setDataLoaded] = useState(false);

  useEffect(() => {
    if (user && !dataLoaded) {
      loadInitialData();
    }
  }, [user, dataLoaded]);

  const loadInitialData = async () => {
    try {
      await getImportStatus();
      setDataLoaded(true);
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  const handleImport = async () => {
    try {
      await startImport();
    } catch (error) {
      console.error('Import failed:', error);
    }
  };

  const loadTopArtists = async () => {
    try {
      const response = await getTopArtists();
      setTopArtists(response.artists || []);
    } catch (error) {
      console.error('Failed to load top artists:', error);
    }
  };

  const loadTopTracks = async () => {
    try {
      const response = await getTopTracks();
      setTopTracks(response.tracks || []);
    } catch (error) {
      console.error('Failed to load top tracks:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Music Atlas
              </h1>
              <div className="text-sm text-gray-400">
                Ciao, {user?.user_profile?.display_name || 'Utente'}!
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Disconnetti
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['overview', 'artists', 'tracks'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-purple-400 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab === 'overview' ? 'Panoramica' : tab === 'artists' ? 'Artisti' : 'Brani'}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {musicError && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-300">{musicError}</p>
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Import Status Card */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Stato Importazione Dati</h2>
              
              {!importStatus?.user_exists ? (
                <div className="text-center py-8">
                  <div className="bg-blue-900/50 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <svg className="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium mb-2">Importa i tuoi dati Spotify</h3>
                  <p className="text-gray-400 mb-4">
                    Per iniziare ad esplorare il tuo grafo musicale, importa i tuoi dati da Spotify
                  </p>
                  <button
                    onClick={handleImport}
                    disabled={importing}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2 mx-auto"
                  >
                    {importing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Importazione in corso...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                        </svg>
                        <span>Avvia Importazione</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-400">
                      {importStatus.statistics?.artists_in_graph || 0}
                    </div>
                    <div className="text-sm text-gray-400">Artisti</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-400">
                      {importStatus.statistics?.tracks_in_graph || 0}
                    </div>
                    <div className="text-sm text-gray-400">Brani</div>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-400">
                      {importStatus.statistics?.albums_in_graph || 0}
                    </div>
                    <div className="text-sm text-gray-400">Album</div>
                  </div>
                </div>
              )}
            </div>

            {/* User Profile Card */}
            {user?.user_profile && (
              <div className="bg-gray-800 rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Il Tuo Profilo Spotify</h2>
                <div className="flex items-center space-x-4">
                  {user.user_profile.images && user.user_profile.images.length > 0 && (
                    <img
                      src={user.user_profile.images[0].url}
                      alt="Profile"
                      className="w-16 h-16 rounded-full"
                    />
                  )}
                  <div>
                    <div className="font-medium">{user.user_profile.display_name}</div>
                    <div className="text-sm text-gray-400">
                      {typeof user.user_profile.followers === 'object' 
                        ? user.user_profile.followers?.total || 0 
                        : user.user_profile.followers || 0} follower
                    </div>
                    <div className="text-sm text-gray-400">ID: {user.user_profile.id}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Artists Tab */}
        {activeTab === 'artists' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">I Tuoi Artisti Preferiti</h2>
              <button
                onClick={loadTopArtists}
                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Carica Artisti
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {topArtists.map((artist, index) => (
                <div key={artist.id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl font-bold text-purple-400">#{index + 1}</div>
                    {artist.images && artist.images.length > 0 && (
                      <img
                        src={artist.images[0].url}
                        alt={artist.name}
                        className="w-12 h-12 rounded-full"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{artist.name}</div>
                      <div className="text-sm text-gray-400">
                        {artist.genres?.slice(0, 2).join(', ') || 'Nessun genere'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tracks Tab */}
        {activeTab === 'tracks' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold">I Tuoi Brani Preferiti</h2>
              <button
                onClick={loadTopTracks}
                className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Carica Brani
              </button>
            </div>
            
            <div className="space-y-2">
              {topTracks.map((track, index) => (
                <div key={track.id} className="bg-gray-800 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-lg font-bold text-green-400 w-8">#{index + 1}</div>
                    {track.album?.images && track.album.images.length > 0 && (
                      <img
                        src={track.album.images[0].url}
                        alt={track.album.name}
                        className="w-12 h-12 rounded"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{track.name}</div>
                      <div className="text-sm text-gray-400 truncate">
                        {track.artists?.map((a: Artist) => a.name).join(', ')} • {track.album?.name}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      {Math.floor(track.duration_ms / 60000)}:{String(Math.floor((track.duration_ms % 60000) / 1000)).padStart(2, '0')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
