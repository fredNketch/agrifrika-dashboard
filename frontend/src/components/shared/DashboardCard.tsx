import React from 'react';
import SmartContentScroll from './SmartContentScroll';
import type { DashboardCardProps } from '../../types';

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  icon,
  children,
  className = '',
  loading = false
}) => {
  return (
    <div className={`card-shadow dashboard-card h-full flex flex-col overflow-hidden bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 transition-colors duration-300 ${className}`}>
      {/* Header - Hauteur fixe */}
      <div className="flex items-center justify-between mb-1 flex-shrink-0">
        <div className="flex items-center space-x-2">
          {icon && (
            <span className="text-lg" role="img" aria-label={title}>
              {icon}
            </span>
          )}
          <h3 className="dashboard-title text-gray-800 dark:text-gray-200 text-sm font-semibold transition-colors duration-300">
            {title}
          </h3>
        </div>
        
        {loading && (
          <div className="flex items-center space-x-1">
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-agrifrika-green"></div>
            <span className="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-300">MAJ...</span>
          </div>
        )}
      </div>
      
      {/* Content - Prend l'espace restant avec défilement intelligent */}
      <div className="dashboard-content flex-1 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="flex flex-col items-center space-y-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-agrifrika-green"></div>
              <span className="text-xs text-gray-500">Chargement...</span>
            </div>
          </div>
        ) : (
          <SmartContentScroll 
            className="h-full"
            scrollSpeed={25}
            pauseDuration={4000}
          >
            {children}
          </SmartContentScroll>
        )}
      </div>
    </div>
  );
};

export default DashboardCard;