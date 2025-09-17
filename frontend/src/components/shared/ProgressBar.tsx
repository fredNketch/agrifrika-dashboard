import React from 'react';
import type { ProgressBarProps } from '../../types';

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  variant = 'green',
  showLabel = true,
  height = 'md'
}) => {
  const percentage = Math.min(Math.max(progress, 0), 100);
  
  const colorClasses = {
    green: 'bg-agrifrika-green',
    orange: 'bg-status-occupied',
    red: 'bg-status-unavailable',
    blue: 'bg-blue-500',
    yellow: 'bg-agrifrika-yellow'
  };
  
  const heightClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4'
  };
  
  return (
    <div className="w-full">
      <div className={`progress-container ${heightClasses[height]}`}>
        <div 
          className={`progress-bar-fill ${colorClasses[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      {showLabel && (
        <div className="flex justify-center mt-1">
          <span className="text-xs text-gray-500">
            {percentage.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;