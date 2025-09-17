import React from 'react';
import { motion } from 'framer-motion';

interface PremiumCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: string;
  loading?: boolean;
  gradient?: boolean;
}

const PremiumCard: React.FC<PremiumCardProps> = ({
  children,
  className = '',
  title,
  icon,
  loading = false,
  gradient = false
}) => {
  const cardClasses = `
    relative overflow-hidden rounded-3xl shadow-xl 
    bg-white dark:bg-gray-800 
    border border-gray-200 dark:border-gray-700
    transition-all duration-300 hover:shadow-2xl hover:-translate-y-1
    ${gradient ? 'bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900' : ''}
    ${className}
  `;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      whileHover={{ y: -4, scale: 1.02 }}
      className={cardClasses}
    >
      {/* Header */}
      {title && (
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            {icon && (
              <span className="text-2xl" role="img" aria-label={title}>
                {icon}
              </span>
            )}
            <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {title}
            </h3>
          </div>
          
          {loading && (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-xs text-gray-500 dark:text-gray-400">Mise à jour...</span>
            </div>
          )}
        </div>
      )}
      
      {/* Content */}
      <div className="p-6">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          children
        )}
      </div>
      
      {/* Gradient overlay for premium effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5 pointer-events-none" />
    </motion.div>
  );
};

export default PremiumCard;