import React, { useState, useEffect, useRef } from 'react';
import AnimatedCard from '../ui/AnimatedCard';
import { FacebookVideoPlayer } from '../shared';
import type { FacebookVideoData } from '../../types';

interface FacebookVideoProps {
  className?: string;
}

const FacebookVideo: React.FC<FacebookVideoProps> = ({ className = '' }) => {
  const [data, setData] = useState<FacebookVideoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    fetchFacebookVideo();
    const interval = setInterval(fetchFacebookVideo, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => {
      clearInterval(interval);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const fetchFacebookVideo = async () => {
    try {
      // Annuler la requête précédente si elle existe
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      abortControllerRef.current = new AbortController();
      setLoading(true);
      
      const response = await fetch('http://192.168.1.45:8000/api/v1/dashboard2/facebook-video', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors',
        signal: abortControllerRef.current.signal
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'API call failed');
      }

      setData(result.data);
      setError(null);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return; // Ignorer les erreurs d'annulation
      }
      setError(err instanceof Error ? err.message : 'Erreur de connexion à l\'API');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const getEngagementColor = (rate: number) => {
    if (rate >= 10) return 'text-green-600 bg-green-50 border-green-200';
    if (rate >= 5) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getEngagementLabel = (rate: number) => {
    if (rate >= 10) return 'Excellent';
    if (rate >= 5) return 'Bon';
    if (rate >= 2) return 'Moyen';
    return 'Faible';
  };

  return (
    <AnimatedCard
      title={data ? `Vidéo ${formatNumber(data.views)} vues` : "Dernière Vidéo"}
      icon="📹"
      loading={loading}
      premium
      className={`h-full ${className}`}
    >
      <div className="h-full flex flex-col">
        {data ? (
          <>
            {/* Lecteur Facebook automatique - Zone agrandie */}
            <div className="flex-1 relative overflow-hidden rounded-lg flex items-center justify-center bg-gray-50 dark:bg-gray-800 p-1">
              {!videoLoaded && (
                <div className="absolute inset-0 flex items-center justify-center z-10">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              )}
            <FacebookVideoPlayer
                videoUrl={data.video_url}
                width={800}
                height={480}
              autoplay={true}
              loop={true}
              allowFullscreen={true}
              showText={false}
              showCaptions={false}
                className="w-full h-full object-contain max-w-full max-h-full"
              onLoad={() => {
                console.log('✅ Vidéo Facebook chargée avec succès');
                  console.log('URL utilisée:', data.video_url);
                  setVideoLoaded(true);
              }}
              onError={(error) => {
                console.error('❌ Erreur vidéo Facebook:', error);
                  console.log('URL problématique:', data.video_url);
                  setVideoLoaded(false);
              }}
            />
          </div>

            {/* Statistiques compactes en bas - Hauteur réduite */}
            <div className="flex justify-center space-x-1 mt-1 h-10">
              <div className="text-center px-2 py-1 bg-blue-50 dark:bg-blue-900/20 rounded text-xs flex flex-col justify-center">
                <div className="text-blue-600 dark:text-blue-400 font-bold">{formatNumber(data.views)}</div>
                <div className="text-blue-500 dark:text-blue-300">Vues</div>
        </div>

              <div className="text-center px-2 py-1 bg-red-50 dark:bg-red-900/20 rounded text-xs flex flex-col justify-center">
                <div className="text-red-600 dark:text-red-400 font-bold">{formatNumber(data.likes)}</div>
            <div className="text-red-500 dark:text-red-300">Likes</div>
              </div>
              
              <div className="text-center px-2 py-1 bg-green-50 dark:bg-green-900/20 rounded text-xs flex flex-col justify-center">
                <div className="text-green-600 dark:text-green-400 font-bold">{formatNumber(data.comments)}</div>
            <div className="text-green-500 dark:text-green-300">Comms</div>
        </div>

              <div className="text-center px-2 py-1 bg-purple-50 dark:bg-purple-900/20 rounded text-xs flex flex-col justify-center">
                <div className="text-purple-600 dark:text-purple-400 font-bold">{data.engagement_rate.toFixed(1)}%</div>
                <div className="text-purple-500 dark:text-purple-300">Engage</div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <div className="text-lg mb-2">📹</div>
              <div className="text-sm">
                {loading ? 'Chargement...' : 'Aucune vidéo disponible'}
              </div>
              <div className="text-xs mt-1">
                {loading ? 'Récupération des données Facebook...' : 'Vérifiez la connexion à l\'API'}
              </div>
          </div>
          </div>
        )}
      </div>
    </AnimatedCard>
  );
};

export default FacebookVideo;