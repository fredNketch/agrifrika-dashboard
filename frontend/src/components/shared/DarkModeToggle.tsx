import React from 'react';
import { motion } from 'framer-motion';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

interface DarkModeToggleProps {
  isDarkMode: boolean;
  onToggle: () => void;
  className?: string;
}

const DarkModeToggle: React.FC<DarkModeToggleProps> = ({
  isDarkMode,
  onToggle,
  className = ''
}) => {
  return (
    <motion.button
      onClick={onToggle}
      className={`
        relative inline-flex items-center justify-center
        w-12 h-12 rounded-full
        bg-white dark:bg-gray-800
        border border-gray-200 dark:border-gray-700
        shadow-md hover:shadow-lg
        transition-all duration-300
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        ${className}
      `}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, rotate: -180 }}
      animate={{ opacity: 1, rotate: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        key={isDarkMode ? 'moon' : 'sun'}
        initial={{ opacity: 0, rotate: 180, scale: 0.5 }}
        animate={{ opacity: 1, rotate: 0, scale: 1 }}
        exit={{ opacity: 0, rotate: -180, scale: 0.5 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-center"
      >
        {isDarkMode ? (
          <MoonIcon className="w-6 h-6 text-blue-400" />
        ) : (
          <SunIcon className="w-6 h-6 text-yellow-500" />
        )}
      </motion.div>
      
      {/* Indicateur d'état */}
      <motion.div
        className={`
          absolute -top-1 -right-1 w-3 h-3 rounded-full
          ${isDarkMode ? 'bg-blue-400' : 'bg-yellow-400'}
        `}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      />
    </motion.button>
  );
};

export default DarkModeToggle;