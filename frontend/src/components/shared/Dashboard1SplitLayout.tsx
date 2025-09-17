import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Dashboard1SplitLayoutProps {
  children: React.ReactNode[];
  rotationInterval?: number; // en secondes
  className?: string;
}

const Dashboard1SplitLayout: React.FC<Dashboard1SplitLayoutProps> = ({
  children,
  rotationInterval = 60, // 60 secondes par défaut
  className = ''
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // Index du prochain bloc (preview)
  const nextIndex = (currentIndex + 1) % children.length;
  
  // Rotation automatique toutes les 60 secondes
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % children.length);
    }, rotationInterval * 1000);

    return () => clearInterval(interval);
  }, [children.length, rotationInterval]);

  // Fonction pour obtenir le titre du bloc
  const getBlockTitle = (index: number) => {
    const titles = ['Default Alive', 'Public Engagement', 'Fundraising Pipeline'];
    return titles[index] || `Bloc ${index + 1}`;
  };

  // Fonction pour obtenir l'icône du bloc
  const getBlockIcon = (index: number) => {
    const icons = ['💰', '👥', '📊'];
    return icons[index] || '📋';
  };

  return (
    <div className={`flex gap-6 h-full ${className}`}>
      {/* Zone principale (2/3) - Bloc courant complet */}
      <div className="flex-[2] relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ 
              duration: 0.8, 
              ease: [0.4, 0, 0.2, 1]
            }}
            className="h-full relative"
          >
            {/* Indicateur de bloc actuel */}
            <div className="absolute top-4 left-4 z-10">
              <div className="flex items-center space-x-3 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-gray-200/50 dark:border-gray-700/50">
                <div className="w-3 h-3 bg-agrifrika-green rounded-full animate-pulse"></div>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getBlockIcon(currentIndex)}</span>
                  <span className="font-semibold text-gray-800 dark:text-gray-100 text-lg">
                    {getBlockTitle(currentIndex)}
                  </span>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300 bg-agrifrika-green/10 dark:bg-agrifrika-green/20 px-2 py-1 rounded-full">
                  ACTUEL
                </div>
              </div>
            </div>

            {/* Barre de progression en bas */}
            <div className="absolute bottom-0 left-0 w-full h-2 bg-gray-200/30 backdrop-blur-sm">
              <motion.div 
                className="h-full bg-gradient-to-r from-agrifrika-green to-agrifrika-yellow rounded-r-full"
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ 
                  duration: rotationInterval,
                  ease: "linear"
                }}
                key={`progress-${currentIndex}`}
              />
            </div>

            {/* Contenu principal */}
            <div className="h-full w-full rounded-2xl overflow-hidden">
              {children[currentIndex]}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Zone preview (1/3) - Prochain bloc */}
      <div className="flex-[1] relative">
        <div className="h-full bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl shadow-modern-lg border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
          
          {/* En-tête preview */}
          <div className="bg-gradient-to-r from-agrifrika-green/10 to-agrifrika-yellow/10 dark:from-agrifrika-green/20 dark:to-agrifrika-yellow/20 p-4 border-b border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getBlockIcon(nextIndex)}</span>
                <div>
                  <h3 className="font-bold text-gray-800 dark:text-gray-100 text-lg">
                    {getBlockTitle(nextIndex)}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Prochainement
                  </p>
                </div>
              </div>
              
              {/* Badge "Suivant" */}
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-3 py-1.5 rounded-full text-sm font-semibold shadow-md">
                SUIVANT
              </div>
            </div>
          </div>

          {/* Contenu preview (version réduite et stylisée) */}
          <div className="p-4 h-full overflow-hidden relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={nextIndex}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ 
                  duration: 0.6,
                  ease: "easeOut",
                  delay: 0.3
                }}
                className="h-full relative"
              >
                {/* Overlay pour créer l'effet preview */}
                <div className="absolute inset-0 bg-gradient-to-t from-white/80 via-transparent to-transparent z-10 pointer-events-none" />
                
                {/* Contenu preview avec effet de réduction */}
                <div className="transform scale-90 origin-top h-full overflow-hidden rounded-xl shadow-inner">
                  {children[nextIndex]}
                </div>

                {/* Indicateur "Preview" flottant */}
                <div className="absolute bottom-4 right-4 z-20">
                  <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-full px-3 py-1.5 shadow-lg border border-gray-200/50 dark:border-gray-700/50">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                      <span className="text-xs font-semibold text-gray-700 dark:text-gray-200">
                        APERÇU
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Compteur de rotation */}
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
          <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-gray-200/50 dark:border-gray-700/50">
            <div className="flex items-center space-x-3">
              {children.map((_, index) => (
                <div
                  key={index}
                  className={`w-3 h-3 rounded-full transition-all duration-500 ${
                    index === currentIndex 
                      ? 'bg-agrifrika-green scale-110 shadow-md' 
                      : index === nextIndex
                        ? 'bg-blue-500 scale-105'
                        : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard1SplitLayout;