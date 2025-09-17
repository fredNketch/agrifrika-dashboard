import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

interface CircularGaugeProps {
  value: number;
  maxValue: number;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  colors?: string[];
  label?: string;
  unit?: string;
  showValue?: boolean;
  animated?: boolean;
  thickness?: number;
}

const CircularGauge: React.FC<CircularGaugeProps> = ({
  value,
  maxValue,
  size = 'md',
  colors = ['#10B981', '#34D399', '#6EE7B7'],
  label,
  unit = '',
  showValue = true,
  animated = true,
  thickness = 20
}) => {
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const sizes = {
    sm: { width: 120, height: 120, fontSize: 'text-lg', labelSize: 'text-xs' },
    md: { width: 180, height: 180, fontSize: 'text-3xl', labelSize: 'text-sm' },
    lg: { width: 240, height: 240, fontSize: 'text-5xl', labelSize: 'text-base' },
    xl: { width: 320, height: 320, fontSize: 'text-7xl', labelSize: 'text-lg' }
  };
  
  const currentSize = sizes[size];
  
  // Données pour le graphique en anneau
  const data = [
    { value: percentage, fill: 'url(#gauge-gradient)' },
    { value: 100 - percentage, fill: '#E5E7EB' }
  ];

  return (
    <div className="relative flex items-center justify-center">
      <svg width="0" height="0">
        <defs>
          <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors[0]} />
            <stop offset="50%" stopColor={colors[1]} />
            <stop offset="100%" stopColor={colors[2] || colors[1]} />
          </linearGradient>
        </defs>
      </svg>
      
      <div style={{ width: currentSize.width, height: currentSize.height }} className="relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={90}
              endAngle={-270}
              innerRadius="70%"
              outerRadius="90%"
              paddingAngle={2}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.fill}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Contenu central */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            {showValue && (
              <motion.div 
                className={`font-bold text-gray-800 dark:text-gray-100 ${currentSize.fontSize}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: animated ? 0.5 : 0, duration: 0.6, type: "spring" }}
              >
                {animated ? (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 0.8 }}
                  >
                    {value.toLocaleString()}{unit}
                  </motion.span>
                ) : (
                  `${value.toLocaleString()}${unit}`
                )}
              </motion.div>
            )}
            
            {label && (
              <motion.div 
                className={`font-medium text-gray-600 dark:text-gray-300 mt-1 ${currentSize.labelSize}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: animated ? 1 : 0, duration: 0.5 }}
              >
                {label}
              </motion.div>
            )}
            
            {/* Pourcentage en petit */}
            <motion.div 
              className="text-xs text-gray-500 dark:text-gray-400 font-semibold mt-1"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: animated ? 1.2 : 0 }}
            >
              {percentage.toFixed(1)}%
            </motion.div>
          </div>
        </div>
        
        {/* Indicateurs de seuil */}
        <div className="absolute inset-0 pointer-events-none">
          {/* Indicateur à 75% */}
          <div 
            className="absolute w-3 h-3 bg-yellow-400 rounded-full border-2 border-white shadow-lg"
            style={{
              top: '15%',
              right: '15%',
              transform: 'translate(50%, -50%)'
            }}
          />
          
          {/* Indicateur à 90% */}
          <div 
            className="absolute w-3 h-3 bg-red-400 rounded-full border-2 border-white shadow-lg"
            style={{
              top: '50%',
              right: '5%',
              transform: 'translate(50%, -50%)'
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default CircularGauge;