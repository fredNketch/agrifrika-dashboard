import React from 'react';
import { motion } from 'framer-motion';
import { DarkModeToggle } from '../shared';
import ThemeSelector from './ThemeSelector';
import { useDarkMode } from '../../hooks/useDarkMode';

interface HeaderProps {
  title?: string;
  showControls?: boolean;
  className?: string;
}

const Header: React.FC<HeaderProps> = ({
  title = "Dashboard Agrifrika",
  showControls = true,
  className = ''
}) => {
  const { isDarkMode, toggle } = useDarkMode();

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`
        sticky top-0 z-50 w-full
        bg-white/80 dark:bg-gray-900/80 
        backdrop-blur-xl border-b border-gray-200 dark:border-gray-700
        shadow-sm
        ${className}
      `}
    >
      <div className="max-w-full mx-auto px-2 py-1">
        <div className="flex items-center justify-between">
          {/* Logo et titre */}
          <motion.div 
            className="flex items-center space-x-4"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <motion.div
              className="relative"
              whileHover={{ rotate: 5 }}
              transition={{ duration: 0.3 }}
            >
              <img
                src={isDarkMode ? "/logo-agrifrika-dark.png" : "/logo-agrifrika.png"}
                alt="Agrifrika Logo"
                className="h-8 w-auto object-contain filter drop-shadow-sm transition-opacity duration-300"
                onError={(e) => {
                  // Fallback si le logo ne charge pas
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
              {/* Cercle de fond avec effet glow */}
              <div className="absolute inset-0 -m-2 bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-full blur-xl -z-10" />
            </motion.div>
            
            <div className="flex flex-col">
              <motion.h1 
                className="text-lg font-bold bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
              >
                {title}
              </motion.h1>
              <motion.p 
                className="text-xs text-gray-500 dark:text-gray-400 font-medium"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                Dashboard opérationel interne
              </motion.p>
            </div>
          </motion.div>

          {/* Contrôles */}
          {showControls && (
            <motion.div 
              className="flex items-center space-x-2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              {/* Indicateur de statut en temps réel */}
              <motion.div 
                className="flex items-center space-x-1 px-2 py-1 rounded-full bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
                animate={{ 
                  boxShadow: [
                    "0 0 0 0 rgba(34, 197, 94, 0.3)",
                    "0 0 0 4px rgba(34, 197, 94, 0.1)",
                    "0 0 0 0 rgba(34, 197, 94, 0.3)"
                  ]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                <span className="text-xs font-medium text-green-700 dark:text-green-300">
                  En direct
                </span>
              </motion.div>

              {/* Sélecteur de thème */}
              <ThemeSelector />

              {/* Toggle mode sombre */}
              <DarkModeToggle
                isDarkMode={isDarkMode}
                onToggle={toggle}
                className="transform hover:scale-105 transition-transform"
              />

              {/* Menu utilisateur simulé */}
              <motion.div
                className="relative"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-green-500 to-blue-600 p-0.5">
                  <div className="w-full h-full rounded-full bg-white dark:bg-gray-800 flex items-center justify-center overflow-hidden">
                    <img
                      src={isDarkMode ? "/logo-agrifrika-dark.png" : "/logo-agrifrika.png"}
                      alt="User Avatar"
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        // Fallback si le logo ne charge pas
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        // Créer un span de fallback
                        const fallback = document.createElement('span');
                        fallback.className = 'text-xs font-bold text-gray-700 dark:text-gray-300';
                        fallback.textContent = 'A';
                        target.parentNode?.appendChild(fallback);
                      }}
                    />
                  </div>
                </div>
                
                {/* Badge de notification */}
                <motion.div
                  className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-red-500 rounded-full flex items-center justify-center"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <span className="text-xs text-white font-bold">3</span>
                </motion.div>
              </motion.div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Barre de progression de chargement */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-green-500 via-blue-500 to-purple-500"
        initial={{ width: "0%" }}
        animate={{ width: "100%" }}
        transition={{ duration: 1.5, ease: "easeOut" }}
      />
    </motion.header>
  );
};

export default Header;