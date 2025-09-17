import React from 'react';
import { motion } from 'framer-motion';

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: string;
  loading?: boolean;
  premium?: boolean;
  delay?: number;
}

const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  className = '',
  title,
  icon,
  loading = false,
  premium = false,
  delay = 0
}) => {
  const cardClasses = `
    relative overflow-hidden rounded-2xl shadow-lg 
    bg-white dark:bg-gray-800 
    border border-gray-200 dark:border-gray-700
    transition-all duration-300 hover:shadow-xl hover:-translate-y-1
    h-full flex flex-col
    ${premium ? 'bg-gradient-to-br from-white via-blue-50 to-purple-50 dark:from-gray-800 dark:via-blue-900/10 dark:to-purple-900/10' : ''}
    ${className}
  `;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.6, 
        delay,
        ease: "easeOut",
        type: "spring",
        stiffness: 100
      }}
      whileHover={{ 
        y: -6, 
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      className={cardClasses}
    >
      {/* Premium shimmer effect */}
      {premium && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 animate-shimmer" />
      )}
      
      {/* Header */}
      {title && (
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-transparent to-blue-50/30 dark:to-blue-900/10">
          <div className="flex items-center space-x-3">
            {icon && (
              <motion.span 
                className="text-2xl filter drop-shadow-sm" 
                role="img" 
                aria-label={title}
                whileHover={{ scale: 1.1, rotate: 5 }}
                transition={{ duration: 0.2 }}
              >
                {icon}
              </motion.span>
            )}
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {title}
            </h3>
          </div>
          
          {loading && (
            <motion.div 
              className="flex items-center space-x-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <div className="relative">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                <div className="absolute inset-0 animate-ping rounded-full h-4 w-4 border border-blue-400 opacity-25"></div>
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">Mise à jour...</span>
            </motion.div>
          )}
        </div>
      )}
      
      {/* Content */}
      <div className="p-6 flex-1 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <motion.div
              className="flex flex-col items-center space-y-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="relative">
                <div className="animate-spin rounded-full h-8 w-8 border-3 border-blue-500 border-t-transparent"></div>
                <div className="absolute inset-0 animate-ping rounded-full h-8 w-8 border border-blue-400 opacity-25"></div>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">Chargement...</span>
            </motion.div>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.4 }}
            className="h-full overflow-hidden"
          >
            {children}
          </motion.div>
        )}
      </div>
      
      {/* Premium glow effect */}
      {premium && (
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-600/5 via-purple-600/5 to-pink-600/5 pointer-events-none" />
      )}
    </motion.div>
  );
};

export default AnimatedCard;