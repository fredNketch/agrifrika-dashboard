import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';

interface TrendData {
  month: string;
  base_points: number;
  activity_points: number;
  total_points: number;
  score: number;
  date: string;
  week: string;
}

interface FundraisingTrendChartProps {
  data: TrendData[];
  height?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white/95 backdrop-blur-sm p-4 border border-gray-200/50 rounded-2xl shadow-2xl">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-sm"></div>
          <p className="font-bold text-gray-800 text-lg">{label}</p>
        </div>
        <div className="space-y-2">
          <div className="flex justify-between items-center bg-gray-50 rounded-lg px-3 py-2">
            <span className="text-sm font-medium text-gray-600">Cumul total</span>
            <span className="font-bold text-xl text-gray-800">{data.total_points} pts</span>
          </div>
          <div className="flex justify-between items-center bg-green-50 rounded-lg px-3 py-2">
            <span className="text-sm font-medium text-gray-600">Évolution</span>
            <span className="font-bold text-lg text-green-600">+{data.activity_points} pts</span>
          </div>
          <div className="flex justify-between items-center bg-blue-50 rounded-lg px-3 py-2">
            <span className="text-sm font-medium text-gray-600">Score</span>
            <span className="font-bold text-lg text-blue-600">{data.score}%</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

const FundraisingTrendChart: React.FC<FundraisingTrendChartProps> = ({ 
  data, 
  height = 120 
}) => {

  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400 text-sm">
        <div className="text-center">
          <div className="animate-pulse text-2xl">📊</div>
          <div className="mt-2 font-medium">Chargement des tendances...</div>
        </div>
      </div>
    );
  }

  // Préparer les données pour le graphique
  const chartData = data.map((item, index) => ({
    ...item,
    value: item.total_points,
    index: index
  }));


  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="w-full h-full relative"
    >
      {/* Graphique principal */}
      <div className="relative">
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 40 }}>
            <defs>
              <linearGradient id="lineGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="50%" stopColor="#8B5CF6" />
                <stop offset="100%" stopColor="#EC4899" />
              </linearGradient>
              <linearGradient id="pointGradient" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#EC4899" />
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" strokeOpacity={0.3} />
            
            <XAxis 
              dataKey="month" 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 13, fill: '#6B7280', fontWeight: 600 }}
              tickMargin={15}
            />
            
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 13, fill: '#6B7280', fontWeight: 600 }}
              domain={['dataMin - 10', 'dataMax + 10']}
              tickMargin={15}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            {/* Ligne principale avec gradient moderne */}
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="url(#lineGradient)"
              strokeWidth={5}
              dot={{ 
                r: 10, 
                stroke: '#fff', 
                strokeWidth: 4, 
                fill: 'url(#pointGradient)',
                filter: 'drop-shadow(0 6px 12px rgba(59, 130, 246, 0.3))'
              }}
              activeDot={{ 
                r: 14, 
                stroke: '#fff', 
                strokeWidth: 4, 
                fill: 'url(#pointGradient)',
                filter: 'drop-shadow(0 8px 16px rgba(59, 130, 246, 0.4))'
              }}
              animationDuration={2000}
            />
          </LineChart>
        </ResponsiveContainer>

      </div>

    </motion.div>
  );
};

export default FundraisingTrendChart;