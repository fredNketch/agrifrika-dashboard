import React from 'react';
import { motion } from 'framer-motion';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  LineChart, 
  Line,
  AreaChart,
  Area
} from 'recharts';

interface ChartData {
  name: string;
  value: number;
  color?: string;
  [key: string]: any;
}

interface ModernChartProps {
  type: 'pie' | 'bar' | 'line' | 'area';
  data: ChartData[];
  height?: number;
  colors?: string[];
  dataKey?: string;
  nameKey?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
  animated?: boolean;
}

const defaultColors = [
  '#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', 
  '#EF4444', '#06B6D4', '#84CC16', '#F97316'
];

const ModernChart: React.FC<ModernChartProps> = ({
  type,
  data,
  height = 300,
  colors = defaultColors,
  dataKey = 'value',
  nameKey = 'name',
  showGrid = true,
  showTooltip = true,
  animated = true
}) => {
  const chartVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1
    }
  };

  const tooltipStyle = {
    background: 'rgba(255, 255, 255, 0.95)',
    border: 'none',
    borderRadius: '12px',
    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    backdropFilter: 'blur(10px)'
  };

  const renderChart = () => {
    switch (type) {
      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              outerRadius={height * 0.3}
              innerRadius={height * 0.15}
              paddingAngle={2}
              dataKey={dataKey}
              animationBegin={animated ? 0 : undefined}
              animationDuration={animated ? 800 : 0}
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.color || colors[index % colors.length]}
                />
              ))}
            </Pie>
            {showTooltip && (
              <Tooltip 
                contentStyle={tooltipStyle}
                formatter={(value) => [`${value}`, 'Valeur']}
              />
            )}
          </PieChart>
        );

      case 'bar':
        return (
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={nameKey} 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            {showTooltip && (
              <Tooltip 
                contentStyle={tooltipStyle}
                formatter={(value) => [`${value}`, 'Valeur']}
              />
            )}
            <Bar 
              dataKey={dataKey} 
              fill={colors[0]}
              radius={[4, 4, 0, 0]}
              animationDuration={animated ? 800 : 0}
            >
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.color || colors[index % colors.length]}
                />
              ))}
            </Bar>
          </BarChart>
        );

      case 'line':
        return (
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={nameKey} 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            {showTooltip && (
              <Tooltip 
                contentStyle={tooltipStyle}
                formatter={(value) => [`${value}`, 'Valeur']}
              />
            )}
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={colors[0]}
              strokeWidth={3}
              dot={{ fill: colors[0], strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: colors[0], strokeWidth: 2, fill: '#ffffff' }}
              animationDuration={animated ? 800 : 0}
            />
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors[0]} stopOpacity={0.8}/>
                <stop offset="95%" stopColor={colors[0]} stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />}
            <XAxis 
              dataKey={nameKey} 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
            />
            {showTooltip && (
              <Tooltip 
                contentStyle={tooltipStyle}
                formatter={(value) => [`${value}`, 'Valeur']}
              />
            )}
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              stroke={colors[0]} 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorGradient)"
              animationDuration={animated ? 800 : 0}
            />
          </AreaChart>
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      variants={chartVariants}
      initial={animated ? "hidden" : undefined}
      animate={animated ? "visible" : undefined}
      transition={{ duration: 0.6, ease: "easeOut" }}
      style={{ height }}
    >
      <ResponsiveContainer width="100%" height="100%">
        {renderChart() || <div>No chart available</div>}
      </ResponsiveContainer>
    </motion.div>
  );
};

export default ModernChart;