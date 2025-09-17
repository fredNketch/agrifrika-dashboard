import React from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line
} from 'recharts';
import { motion } from 'framer-motion';

interface AnimatedChartProps {
  type: 'area' | 'pie' | 'bar' | 'line';
  data: any[];
  width?: string;
  height?: number;
  colors?: string[];
  gradient?: boolean;
  animated?: boolean;
  config?: {
    xKey?: string;
    yKey?: string;
    nameKey?: string;
    valueKey?: string;
  };
}

const AnimatedChart: React.FC<AnimatedChartProps> = ({
  type,
  data,
  width = "100%",
  height = 200,
  colors = ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444'],
  gradient = true,
  animated = true,
  config = {}
}) => {
  const {
    xKey = 'name',
    yKey = 'value',
    nameKey = 'name',
    valueKey = 'value'
  } = config;

  // Tooltip personnalisé
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white p-3 rounded-lg shadow-lg border border-gray-200"
        >
          <p className="font-semibold text-gray-800">{`${label}`}</p>
          {payload.map((pld: any, index: number) => (
            <p key={index} style={{ color: pld.color }} className="font-medium">
              {`${pld.name}: ${pld.value.toLocaleString()}`}
            </p>
          ))}
        </motion.div>
      );
    }
    return null;
  };

  // Rendu du graphique Area
  const renderAreaChart = () => (
    <ResponsiveContainer width={width} height={height}>
      <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          {gradient && (
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={colors[0]} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={colors[0]} stopOpacity={0.1}/>
            </linearGradient>
          )}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey={xKey} 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Area 
          type="monotone" 
          dataKey={yKey} 
          stroke={colors[0]}
          strokeWidth={3}
          fillOpacity={1} 
          fill={gradient ? "url(#colorGradient)" : colors[0]}
          dot={{ r: 6, stroke: colors[0], strokeWidth: 2, fill: '#fff' }}
          activeDot={{ r: 8, stroke: colors[0], strokeWidth: 2, fill: colors[0] }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );

  // Rendu du graphique Pie (Donut)
  const renderPieChart = () => (
    <ResponsiveContainer width={width} height={height}>
      <PieChart>
        <defs>
          {colors.map((color, index) => (
            <linearGradient key={index} id={`pieGradient${index}`} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={1}/>
              <stop offset="100%" stopColor={color} stopOpacity={0.6}/>
            </linearGradient>
          ))}
        </defs>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={3}
          dataKey={valueKey}
          animationBegin={animated ? 0 : undefined}
          animationDuration={animated ? 1500 : 0}
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={gradient ? `url(#pieGradient${index % colors.length})` : colors[index % colors.length]}
              stroke="white"
              strokeWidth={2}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  );

  // Rendu du graphique Bar
  const renderBarChart = () => (
    <ResponsiveContainer width={width} height={height}>
      <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <defs>
          {gradient && (
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={colors[0]} stopOpacity={1}/>
              <stop offset="95%" stopColor={colors[0]} stopOpacity={0.6}/>
            </linearGradient>
          )}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey={xKey} 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar 
          dataKey={yKey} 
          fill={gradient ? "url(#barGradient)" : colors[0]}
          radius={[4, 4, 0, 0]}
          animationDuration={animated ? 1200 : 0}
        />
      </BarChart>
    </ResponsiveContainer>
  );

  // Rendu du graphique Line
  const renderLineChart = () => (
    <ResponsiveContainer width={width} height={height}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey={xKey} 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#6B7280' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line 
          type="monotone" 
          dataKey={yKey} 
          stroke={colors[0]}
          strokeWidth={3}
          dot={{ r: 6, stroke: colors[0], strokeWidth: 2, fill: '#fff' }}
          activeDot={{ r: 8, stroke: colors[0], strokeWidth: 2, fill: colors[0] }}
          animationDuration={animated ? 1500 : 0}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  const renderChart = () => {
    switch (type) {
      case 'area':
        return renderAreaChart();
      case 'pie':
        return renderPieChart();
      case 'bar':
        return renderBarChart();
      case 'line':
        return renderLineChart();
      default:
        return renderAreaChart();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="w-full"
    >
      {renderChart()}
    </motion.div>
  );
};

export default AnimatedChart;