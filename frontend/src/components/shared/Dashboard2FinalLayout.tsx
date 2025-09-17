import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Dashboard2FinalLayoutProps {
  // Zone 1 - Rotation entre 2 composants
  teamAvailability: React.ReactNode;
  weeklyPlanning: React.ReactNode;
  
  // Zone 2 - Seulement les todos (pas de rotation avec ActionPlan)
  basecampTodos: React.ReactNode;
  
  // Zone 3 - 2 composants fixes
  facebookVideo: React.ReactNode;  // Haut
  cashFlow: React.ReactNode;       // Bas
  
  rotationInterval?: number; // en secondes
}

const Dashboard2FinalLayout: React.FC<Dashboard2FinalLayoutProps> = ({
  teamAvailability,
  weeklyPlanning,
  basecampTodos,
  facebookVideo,
  cashFlow,
  rotationInterval = 30
}) => {
  // États de rotation pour chaque zone
  const [zone1Index, setZone1Index] = useState(0); // TeamAvailability ⟷ WeeklyPlanning

  // Rotation automatique pour la zone 1
  useEffect(() => {
    const interval = setInterval(() => {
      setZone1Index(prev => (prev + 1) % 2);
    }, rotationInterval * 1000);
    return () => clearInterval(interval);
  }, [rotationInterval]);

  // Composants pour chaque zone
  const zone1Components = [teamAvailability, weeklyPlanning];
  
  const zone1Labels = ['Disponibilité Équipe', 'Planning Hebdomadaire'];

  // Indicateur de rotation
  const renderRotationIndicator = (currentIndex: number, totalComponents: number, label: string, zone: string) => (
    <motion.div 
      className="absolute top-2 right-2 z-20 flex items-center space-x-2 bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-full px-3 py-1 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.5 }}
    >
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
      <span className="text-xs font-semibold text-gray-700 dark:text-gray-200">
        {label}
      </span>
      <div className="flex space-x-1">
        {Array.from({ length: totalComponents }).map((_, index) => (
          <motion.div
            key={`${zone}-${index}`}
            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
              index === currentIndex ? 'bg-blue-500 scale-125' : 'bg-gray-300 dark:bg-gray-600'
            }`}
            animate={index === currentIndex ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 0.5, repeat: Infinity }}
          />
        ))}
      </div>
    </motion.div>
  );

  // Barre de progression de rotation
  const renderProgressBar = (zoneKey: string) => (
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
        key={`${zoneKey}-progress`}
      />
    </div>
  );

  return (
    <motion.div 
      className="h-full grid grid-cols-3 gap-4 p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Zone 1 - 1er tiers : TeamAvailability ⟷ WeeklyPlanning */}
      <div className="relative w-full">
        {renderRotationIndicator(zone1Index, 2, zone1Labels[zone1Index], 'zone1')}
        {renderProgressBar('zone1')}
        
        <AnimatePresence mode="wait">
          <motion.div
            key={`zone1-${zone1Index}`}
            initial={{ opacity: 0, rotateY: -15, scale: 0.95 }}
            animate={{ opacity: 1, rotateY: 0, scale: 1 }}
            exit={{ opacity: 0, rotateY: 15, scale: 0.95 }}
            transition={{ 
              duration: 0.6,
              ease: "easeInOut"
            }}
            className="h-full"
          >
            {zone1Components[zone1Index]}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Zone 2 - 2ème tiers : BasecampTodos (fixe) */}
      <div className="relative w-full">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="h-full"
        >
          {basecampTodos}
        </motion.div>
      </div>

      {/* Zone 3 - 3ème tiers : FacebookVideo (haut) + CashFlow (bas) */}
      <div className="flex flex-col gap-4 w-full">
        {/* Facebook Video - Partie haute (fixe) */}
        <motion.div 
          className="flex-1 relative"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {facebookVideo}
        </motion.div>

        {/* Cash Flow - Partie basse (fixe) */}
        <motion.div 
          className="flex-1 relative"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          {cashFlow}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Dashboard2FinalLayout;