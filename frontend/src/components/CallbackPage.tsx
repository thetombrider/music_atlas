import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';

const CallbackPage: React.FC = () => {
  const { handleCallback } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processCallback = async () => {
      try {
        // Estrai parametri dall'URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const errorParam = urlParams.get('error');

        if (errorParam) {
          throw new Error(`Spotify authorization error: ${errorParam}`);
        }

        if (!code) {
          throw new Error('Authorization code not found');
        }

        // Gestisci il callback
        await handleCallback(code, state || undefined);
        setStatus('success');

        // Reindirizza alla dashboard dopo 2 secondi
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);

      } catch (error: any) {
        console.error('Callback processing failed:', error);
        setError(error.message || 'Authorization failed');
        setStatus('error');
      }
    };

    processCallback();
  }, [handleCallback]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 max-w-md w-full shadow-2xl border border-white/20 text-center">
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-400 mx-auto mb-6"></div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Connessione in corso...
            </h1>
            <p className="text-gray-300">
              Stiamo completando l'autenticazione con Spotify
            </p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="bg-green-500 rounded-full w-16 h-16 mx-auto mb-6 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Connessione riuscita!
            </h1>
            <p className="text-gray-300 mb-4">
              Il tuo account Spotify è stato collegato con successo
            </p>
            <p className="text-sm text-gray-400">
              Reindirizzamento alla dashboard...
            </p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="bg-red-500 rounded-full w-16 h-16 mx-auto mb-6 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">
              Errore di connessione
            </h1>
            <p className="text-gray-300 mb-4">
              {error || 'Si è verificato un errore durante l\'autenticazione'}
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Torna al login
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default CallbackPage;
