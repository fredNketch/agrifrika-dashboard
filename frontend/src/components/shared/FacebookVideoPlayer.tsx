import React, { useEffect, useMemo, useRef, useState } from 'react';

interface FacebookVideoPlayerProps {
  videoUrl: string;
  width?: number;
  height?: number;
  autoplay?: boolean;
  loop?: boolean;
  allowFullscreen?: boolean;
  showText?: boolean;
  showCaptions?: boolean;
  lazy?: boolean;
  className?: string;
  onLoad?: () => void;
  onError?: (error: string) => void;
}

/**
 * Transforme une URL Facebook en format embed
 */
function transformFacebookUrl(originalUrl: string): string {
  if (!originalUrl) return '';
  
  let cleanUrl = originalUrl.trim();
  
  // Conversion web.facebook.com vers www.facebook.com
  if (cleanUrl.includes('web.facebook.com')) {
    cleanUrl = cleanUrl.replace('web.facebook.com', 'www.facebook.com');
  }
  
  return cleanUrl;
}

const FacebookVideoPlayer: React.FC<FacebookVideoPlayerProps> = ({
  videoUrl,
  width = 500,
  height = 300,
  autoplay = true,
  loop = true,
  allowFullscreen = true,
  showText = false,
  showCaptions = false,
  lazy = false,
  className = "",
  onLoad,
  onError
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const transformedUrl = useMemo(() => transformFacebookUrl(videoUrl), [videoUrl]);

  // URL embed Facebook simple
  const embedUrl = useMemo(() => {
    if (!transformedUrl) return '';
    
    // Utiliser des dimensions plus grandes pour une meilleure qualité
    const embedWidth = Math.max(width, 800);
    const embedHeight = Math.max(height, 480);
    
    const params = new URLSearchParams({
      href: transformedUrl,
      show_text: showText ? 'true' : 'false',
      width: embedWidth.toString(),
      height: embedHeight.toString(),
      autoplay: autoplay ? 'true' : 'false',
      muted: 'true'
    });
    
    return `https://www.facebook.com/plugins/video.php?${params.toString()}`;
  }, [transformedUrl, width, height, showText, autoplay]);

  useEffect(() => {
    console.log('🎬 Facebook Video Player');
    console.log('URL originale:', videoUrl);
    console.log('URL embed:', embedUrl);
    onLoad?.();
  }, [videoUrl, embedUrl, onLoad]);

  return (
    <div
      className={`facebook-video-player ${className} relative w-full h-full`}
      style={{ minWidth: `${width}px`, minHeight: `${height}px` }}
    >
      {/* IFRAME FACEBOOK */}
      <iframe
        ref={iframeRef}
        src={embedUrl}
        width="100%"
        height="100%"
        style={{ 
          border: 'none', 
          overflow: 'hidden',
          borderRadius: '12px',
          width: '100%',
          height: '100%'
        }}
        scrolling="no"
        frameBorder="0"
        allowFullScreen={allowFullscreen}
        allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"
        title="Facebook Video"
        loading="eager"
        onLoad={() => {
          console.log('✅ Iframe Facebook chargée');
          setIsLoading(false);
        }}
        onError={(e) => {
          console.error('❌ Erreur iframe Facebook:', e);
          setIsLoading(false);
          onError?.('Erreur chargement vidéo Facebook');
        }}
      />

      {/* Loader simple */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}
      
    </div>
  );
};

export default FacebookVideoPlayer;