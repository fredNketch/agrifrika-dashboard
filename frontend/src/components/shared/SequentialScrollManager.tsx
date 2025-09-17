import React, { useState, useEffect } from 'react';
import { AutoScrollContainer } from './index';

interface SequentialScrollManagerProps {
  children: React.ReactNode[];
  rotationInterval?: number; // en secondes
  scrollSpeed?: number;
  className?: string;
}

const SequentialScrollManager: React.FC<SequentialScrollManagerProps> = ({
  children,
  rotationInterval = 18, // 18 secondes par bloc
  scrollSpeed = 15,
  className = ''
}) => {
  const [activeScrollIndex, setActiveScrollIndex] = useState(0);
  
  // Rotation automatique entre les blocs
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveScrollIndex(prev => (prev + 1) % children.length);
    }, rotationInterval * 1000);

    return () => clearInterval(interval);
  }, [children.length, rotationInterval]);

  // Fonction pour créer l'indicateur visuel
  const renderScrollIndicator = () => (
    <div className="scroll-indicator">
      {children.map((_, index) => (
        <div
          key={index}
          className={`scroll-indicator-dot ${
            index === activeScrollIndex ? 'active' : 'inactive'
          }`}
          title={`Bloc ${index + 1} ${index === activeScrollIndex ? '(en cours de défilement)' : ''}`}
        />
      ))}
    </div>
  );

  return (
    <div className={`grid grid-cols-3 gap-3 h-full ${className}`}>
      {children.map((child, index) => (
        <div key={index} className="relative h-full">
          {/* Indicateur de défilement actif - toujours visible mais discret */}
          {renderScrollIndicator()}
          
          {/* Conteneur avec défilement conditionnel */}
          <div className={`h-full transition-all duration-500 ${
            index === activeScrollIndex 
              ? 'ring-2 ring-blue-400/30 shadow-lg' 
              : 'opacity-95'
          }`}>
            {index === activeScrollIndex ? (
              <AutoScrollContainer 
                className="h-full" 
                scrollSpeed={scrollSpeed}
                pauseOnHover={true}
              >
                {child}
              </AutoScrollContainer>
            ) : (
              <div className="h-full overflow-hidden">
                {child}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SequentialScrollManager;