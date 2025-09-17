import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Dashboard2RotatingLayoutProps {
  permanentBlocks: {
    topLeft: React.ReactNode;
    topRight?: React.ReactNode;
    bottomRight: React.ReactNode;
  };
  rotatingBlocks: React.ReactNode[];
  rotationInterval?: number; // en secondes
}

const Dashboard2RotatingLayout: React.FC<Dashboard2RotatingLayoutProps> = ({
  permanentBlocks,
  rotatingBlocks,
  rotationInterval = 30
}) => {
  const [currentRotationIndex, setCurrentRotationIndex] = useState(0);

  // Rotation automatique des blocs rotatifs (1 visible à la fois)
  useEffect(() => {
    if (rotatingBlocks.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentRotationIndex(prev => (prev + 1) % rotatingBlocks.length);
    }, rotationInterval * 1000);

    return () => clearInterval(interval);
  }, [rotatingBlocks.length, rotationInterval]);

  // Obtenir le bloc rotatif actuel (seulement 1 slot rotatif maintenant)
  const getVisibleRotatingBlock = () => {
    if (rotatingBlocks.length === 0) return null;
    return rotatingBlocks[currentRotationIndex % rotatingBlocks.length];
  };

  const bottomLeft = getVisibleRotatingBlock();

  // Indicateur de rotation amélioré
  const renderRotationIndicator = () => {
    if (rotatingBlocks.length <= 1) return null;

    return (
      <motion.div 
        className="absolute top-4 right-4 z-20 flex items-center space-x-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-3 py-2 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
        <span className="text-xs font-semibold text-gray-700 dark:text-gray-200">
          {currentRotationIndex + 1}/{rotatingBlocks.length}
        </span>
        <div className="flex space-x-1">
          {rotatingBlocks.map((_, index) => (
            <motion.div
              key={index}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                index === currentRotationIndex
                  ? 'bg-blue-500 scale-125'
                  : 'bg-gray-300 dark:bg-gray-600'
              }`}
              animate={index === currentRotationIndex ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 0.5, repeat: Infinity }}
            />
          ))}
        </div>
      </motion.div>
    );
  };

  return (
    <motion.div 
      className="relative h-full grid grid-cols-2 grid-rows-2 gap-4 p-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Indicateur de rotation */}
      {renderRotationIndicator()}

      {/* Top Left - Permanent */}
      <motion.div 
        className="relative"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
      >
        {permanentBlocks.topLeft}
      </motion.div>

      {/* Top Right - Permanent */}
      <motion.div 
        className="relative"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        {permanentBlocks.topRight || (
          <div className="dashboard-card h-full flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm">
            Pas de bloc assigné
          </div>
        )}
      </motion.div>

      {/* Bottom Left - Rotatif avec animations */}
      <motion.div 
        className="relative"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <AnimatePresence mode="wait">
          {bottomLeft ? (
            <motion.div
              key={`rotating-${currentRotationIndex}`}
              initial={{ opacity: 0, scale: 0.9, rotateY: -10 }}
              animate={{ opacity: 1, scale: 1, rotateY: 0 }}
              exit={{ opacity: 0, scale: 0.9, rotateY: 10 }}
              transition={{ 
                duration: 0.5,
                ease: "easeInOut"
              }}
              className="h-full"
            >
              {bottomLeft}
            </motion.div>
          ) : (
            <motion.div 
              className="dashboard-card h-full flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent mx-auto mb-2"></div>
                Bloc en rotation...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Indicateur de progression de rotation */}
        <div className="absolute bottom-0 left-0 w-full h-1 bg-gray-200/30 dark:bg-gray-700/30 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ 
              duration: rotationInterval,
              ease: "linear",
              repeat: Infinity
            }}
            key={`progress-${currentRotationIndex}`}
          />
        </div>
      </motion.div>

      {/* Bottom Right - Permanent */}
      <motion.div 
        className="relative"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {permanentBlocks.bottomRight}
      </motion.div>
    </motion.div>
  );
};

export default Dashboard2RotatingLayout;