import React, { useState, useEffect } from 'react';
import type { RotatingContentProps } from '../../types';

const RotatingContent: React.FC<RotatingContentProps> = ({
  views,
  autoRotate = true
}) => {
  const [currentViewIndex, setCurrentViewIndex] = useState(0);
  
  useEffect(() => {
    if (!autoRotate || views.length <= 1) return;
    
    const currentView = views[currentViewIndex];
    const timer = setTimeout(() => {
      setCurrentViewIndex((prevIndex) => 
        (prevIndex + 1) % views.length
      );
    }, currentView.duration * 1000);
    
    return () => clearTimeout(timer);
  }, [currentViewIndex, views, autoRotate]);
  
  if (views.length === 0) return null;
  
  const currentView = views[currentViewIndex];
  
  return (
    <div className="relative w-full h-full">
      {/* Content */}
      <div className="transition-all duration-500 ease-in-out">
        {currentView.component}
      </div>
      
      {/* Rotation indicators */}
      {views.length > 1 && (
        <div className="absolute bottom-2 right-2 flex space-x-1">
          {views.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentViewIndex 
                  ? 'bg-agrifrika-green scale-110' 
                  : 'bg-gray-300 hover:bg-gray-400'
              }`}
              onClick={() => setCurrentViewIndex(index)}
              style={{ cursor: 'pointer' }}
            />
          ))}
        </div>
      )}
      
      {/* Progress bar pour la rotation actuelle */}
      {autoRotate && views.length > 1 && (
        <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-200">
          <div 
            className="h-full bg-agrifrika-green transition-all ease-linear"
            style={{
              width: '0%',
              animation: `progress ${currentView.duration}s linear`
            }}
          />
        </div>
      )}
      
      <style>{`
        @keyframes progress {
          from { width: 0%; }
          to { width: 100%; }
        }
      `}</style>
    </div>
  );
};

export default RotatingContent;