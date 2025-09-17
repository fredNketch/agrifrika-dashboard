import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Dashboard2FullscreenLayoutProps {
  teamAvailability: React.ReactNode;
  weeklyPlanning: React.ReactNode;
  basecampTodos: React.ReactNode;
  facebookVideo: React.ReactNode;
  cashFlow: React.ReactNode;
  actionPlan?: React.ReactNode; // Optionnel maintenant
  rotationInterval?: number; // en secondes (défaut: 180 = 3 minutes)
}

const Dashboard2FullscreenLayout: React.FC<Dashboard2FullscreenLayoutProps> = ({
  teamAvailability,
  weeklyPlanning,
  basecampTodos,
  facebookVideo,
  cashFlow,
  actionPlan,
  rotationInterval = 180 // 3 minutes par défaut
}) => {
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [showControls, setShowControls] = useState(false);

  // Tous les blocs disponibles avec leurs temps d'affichage personnalisés
  const blocks = [
    { component: teamAvailability, name: 'Disponibilité Équipe', icon: '👥', duration: 180 }, // 3 minutes
    { component: weeklyPlanning, name: 'Planning Hebdomadaire', icon: '📅', duration: 180 }, // 3 minutes
    { component: basecampTodos, name: 'Tâches Basecamp', icon: '✅', duration: 540 }, // 9 minutes
    { component: facebookVideo, name: 'Vidéo Facebook', icon: '📹', duration: 180 }, // 3 minutes
    { component: cashFlow, name: 'Flux de Trésorerie', icon: '💰', duration: 180 } // 3 minutes
  ];

  // Rotation automatique avec durées personnalisées
  useEffect(() => {
    const currentBlock = blocks[currentBlockIndex];
    const duration = currentBlock.duration;
    
    const interval = setInterval(() => {
      setCurrentBlockIndex(prev => (prev + 1) % blocks.length);
    }, duration * 1000);
    
    return () => clearInterval(interval);
  }, [currentBlockIndex, blocks.length]);

  // Navigation clavier
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') {
        setCurrentBlockIndex(prev => (prev - 1 + blocks.length) % blocks.length);
      } else if (event.key === 'ArrowRight') {
        setCurrentBlockIndex(prev => (prev + 1) % blocks.length);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [blocks.length]);

  // Indicateur de progression
  const renderProgressIndicator = () => (
    <motion.div 
      className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 flex items-center space-x-4 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-6 py-3 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: showControls ? 1 : 0, y: showControls ? 0 : -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center space-x-2">
        <span className="text-lg">{blocks[currentBlockIndex].icon}</span>
        <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">
          {blocks[currentBlockIndex].name}
        </span>
      </div>
      
      <div className="flex items-center space-x-2">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {currentBlockIndex + 1}/{blocks.length}
        </span>
        <div className="flex space-x-1">
          {blocks.map((_, index) => (
            <motion.div
              key={index}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentBlockIndex ? 'bg-blue-500 scale-125' : 'bg-gray-300 dark:bg-gray-600'
              }`}
              animate={index === currentBlockIndex ? { scale: [1, 1.3, 1] } : {}}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );

  // Barre de progression temporelle
  const renderTimeProgressBar = () => {
    const currentBlock = blocks[currentBlockIndex];
    const duration = currentBlock.duration;
    
    return (
      <div className="absolute bottom-4 left-4 right-4 h-2 bg-gray-200/30 dark:bg-gray-700/30 rounded-full overflow-hidden">
        <motion.div 
          className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"
          initial={{ width: "0%" }}
          animate={{ width: "100%" }}
          transition={{ 
            duration: duration,
            ease: "linear",
            repeat: Infinity
          }}
          key={`progress-${currentBlockIndex}`}
        />
      </div>
    );
  };

  // Compteur de temps restant
  const renderTimeCounter = () => {
    const currentBlock = blocks[currentBlockIndex];
    const duration = currentBlock.duration;
    const [timeLeft, setTimeLeft] = useState(duration);

    useEffect(() => {
      setTimeLeft(duration);
      const interval = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) return duration;
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(interval);
    }, [currentBlockIndex, duration]);

    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;

    return (
      <motion.div 
        className="absolute top-4 right-4 z-20 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: showControls ? 1 : 0, scale: showControls ? 1 : 0.9 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <div className="text-sm font-mono text-gray-700 dark:text-gray-200">
            {minutes.toString().padStart(2, '0')}:{seconds.toString().padStart(2, '0')}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div 
      className="relative h-full w-full"
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      {/* Indicateur de progression */}
      {renderProgressIndicator()}
      
      {/* Compteur de temps */}
      {renderTimeCounter()}
      
      {/* Boutons de navigation */}
      <motion.div 
        className="absolute top-1/2 left-4 transform -translate-y-1/2 z-20"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: showControls ? 1 : 0, x: showControls ? 0 : -20 }}
        transition={{ duration: 0.3 }}
      >
        <button
          onClick={() => setCurrentBlockIndex(prev => (prev - 1 + blocks.length) % blocks.length)}
          className="bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-800 backdrop-blur-sm rounded-full p-3 shadow-lg border border-gray-200/50 dark:border-gray-700/50 transition-all duration-200 hover:scale-110"
          title="Bloc précédent (←)"
        >
          <svg className="w-6 h-6 text-gray-700 dark:text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </motion.div>

      <motion.div 
        className="absolute top-1/2 right-4 transform -translate-y-1/2 z-20"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: showControls ? 1 : 0, x: showControls ? 0 : 20 }}
        transition={{ duration: 0.3 }}
      >
        <button
          onClick={() => setCurrentBlockIndex(prev => (prev + 1) % blocks.length)}
          className="bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-800 backdrop-blur-sm rounded-full p-3 shadow-lg border border-gray-200/50 dark:border-gray-700/50 transition-all duration-200 hover:scale-110"
          title="Bloc suivant (→)"
        >
          <svg className="w-6 h-6 text-gray-700 dark:text-gray-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </motion.div>
      
      {/* Barre de progression temporelle */}
      {renderTimeProgressBar()}

      {/* Contenu principal - Rotation plein écran */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`block-${currentBlockIndex}`}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.05 }}
          transition={{ 
            duration: 0.8,
            ease: "easeInOut"
          }}
          className="h-full w-full"
        >
          {blocks[currentBlockIndex].component}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default Dashboard2FullscreenLayout;
