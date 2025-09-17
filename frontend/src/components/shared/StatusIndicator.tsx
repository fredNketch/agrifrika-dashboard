import React from 'react';
import type { StatusIndicatorProps } from '../../types';

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  size = 'md'
}) => {
  const statusConfig = {
    available: {
      icon: '💻',
      text: 'Online',
      className: 'status-available'
    },
    occupied: {
      icon: '🏢',
      text: 'Office',
      className: 'status-occupied'
    },
    unavailable: {
      icon: '❌',
      text: 'Unavailable',
      className: 'status-unavailable'
    },
    field: {
      icon: '🚗',
      text: 'Field',
      className: 'status-occupied'
    }
  };
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };
  
  const config = statusConfig[status];
  const displayText = label || config.text;
  
  return (
    <div className={`status-indicator ${config.className} ${sizeClasses[size]}`}>
      <span className="mr-2" role="img" aria-label={status}>
        {config.icon}
      </span>
      <span className="font-medium">
        {displayText}
      </span>
    </div>
  );
};

export default StatusIndicator;