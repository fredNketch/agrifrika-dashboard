import React, { useEffect, useRef, useState } from 'react';

interface SmartContentScrollProps {
  children: React.ReactNode;
  scrollSpeed?: number; // pixels par seconde
  pauseDuration?: number; // durée de pause en millisecondes
  className?: string;
}

const SmartContentScroll: React.FC<SmartContentScrollProps> = ({
  children,
  scrollSpeed = 20,
  pauseDuration = 3000, // 3 secondes de pause par défaut
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [scrollState, setScrollState] = useState<'paused' | 'scrolling' | 'resetting'>('paused');
  const [currentPosition, setCurrentPosition] = useState(0);
  const animationRef = useRef<number | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    const content = contentRef.current;
    
    if (!container || !content) return;

    const containerHeight = container.clientHeight;
    const contentHeight = content.scrollHeight;
    const maxScroll = contentHeight - containerHeight;

    // Si le contenu tient entièrement, pas besoin de scroll
    if (maxScroll <= 0) {
      return;
    }

    const startScrollCycle = () => {
      // Phase 1: Pause initiale (lecture du début)
      setScrollState('paused');
      timeoutRef.current = setTimeout(() => {
        setScrollState('scrolling');
        scroll();
      }, pauseDuration);
    };

    const scroll = () => {
      if (scrollState !== 'scrolling') return;

      const newPosition = Math.min(currentPosition + (scrollSpeed / 60), maxScroll);
      setCurrentPosition(newPosition);
      container.scrollTop = newPosition;

      // Si on a atteint la fin
      if (newPosition >= maxScroll) {
        setScrollState('paused');
        // Pause à la fin pour lire le contenu final
        timeoutRef.current = setTimeout(() => {
          // Reset smooth vers le haut
          setScrollState('resetting');
          container.scrollTo({ top: 0, behavior: 'smooth' });
          setCurrentPosition(0);
          
          // Recommencer le cycle après reset
          setTimeout(startScrollCycle, 1500);
        }, pauseDuration);
      } else {
        animationRef.current = requestAnimationFrame(scroll);
      }
    };

    // Démarrer le premier cycle
    startScrollCycle();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [scrollSpeed, pauseDuration, scrollState, currentPosition]);

  // Indicateur visuel du statut de défilement
  const renderScrollIndicator = () => {
    const container = containerRef.current;
    const content = contentRef.current;
    
    if (!container || !content) return null;
    
    const maxScroll = content.scrollHeight - container.clientHeight;
    if (maxScroll <= 0) return null;

    const progress = (currentPosition / maxScroll) * 100;

    return (
      <div className="absolute top-1 right-1 z-10 flex items-center space-x-1">
        {/* Barre de progression */}
        <div className="w-8 h-1 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-500 transition-all duration-200"
            style={{ width: `${progress}%` }}
          />
        </div>
        
        {/* Indicateur de statut */}
        <div className={`w-2 h-2 rounded-full transition-colors duration-300 ${
          scrollState === 'paused' ? 'bg-orange-400' :
          scrollState === 'scrolling' ? 'bg-green-400' :
          'bg-blue-400'
        }`} />
      </div>
    );
  };

  return (
    <div className={`relative ${className}`}>
      {renderScrollIndicator()}
      
      <div 
        ref={containerRef}
        className="h-full overflow-hidden scrollbar-hide"
        style={{ 
          scrollbarWidth: 'none', 
          msOverflowStyle: 'none'
        }}
      >
        <div ref={contentRef} className="w-full">
          {children}
        </div>
      </div>
    </div>
  );
};

export default SmartContentScroll;