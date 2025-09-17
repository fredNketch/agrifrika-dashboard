import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
  LabelList
} from 'recharts';

interface PublicEngagementTrendChartProps {
  data: Array<{
    month: string;
    score: number;
    total_score?: number;
    entries_count?: number;
    total_vues?: number;
    total_likes?: number;
    total_partages?: number;
    total_commentaires?: number;
    total_abonnes?: number;
    month_key?: string;
  }>;
  height?: number;
}

const PublicEngagementTrendChart: React.FC<PublicEngagementTrendChartProps> = ({
  data,
  height = 120
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400 text-sm">
        <div className="text-center">
          <div className="animate-pulse text-2xl">📊</div>
          <div className="text-xs mt-1">Aucune donnée de tendance</div>
        </div>
      </div>
    );
  }

  // Préparer les données pour le graphique
  const chartData = data.map((item, index) => ({
    ...item,
    // Utiliser en priorité les points mensuels calculés côté backend
    value: (item as any).total_score ?? item.score ?? 0,
    index: index
  }));

  // Configuration du tooltip personnalisé - Version sécurisée
  const CustomTooltip = ({ active, payload, label }: any) => {
    try {
      if (active && payload && payload.length && payload[0] && payload[0].payload) {
        const tooltipData = payload[0].payload;
        return (
          <div className="bg-white p-2 rounded-lg shadow-lg border border-gray-200">
            <div className="text-xs font-bold text-gray-800 mb-1">{label}</div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-600">Points:</span>
                <span className="font-bold text-purple-600">{(tooltipData.total_score ?? tooltipData.score ?? 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Vues:</span>
                <span className="font-bold text-blue-600">{tooltipData.total_vues?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Likes:</span>
                <span className="font-bold text-green-600">{tooltipData.total_likes?.toLocaleString() || '0'}</span>
              </div>
            </div>
          </div>
        );
      }
    } catch (error) {
      console.error('Tooltip error:', error);
    }
    return null;
  };

  // Calculer la tendance (évolution entre le mois précédent et le mois actuel)
  // Prendre les 2 derniers mois pour le calcul de progression
  const lastTwoMonths = chartData.slice(-2);
  const previousValue = lastTwoMonths[0]?.value || 0;
  const currentValue = lastTwoMonths[1]?.value || 0;

  // Debug: Vérifier les valeurs
  console.log('=== DEBUG TREND CHART ===');
  console.log('data reçu:', data);
  console.log('chartData mappé:', chartData);
  console.log('previousValue:', previousValue, 'currentValue:', currentValue);
  console.log('Valeurs score brutes:', data.map(d => d.score));

  // Calculer la progression par rapport au mois précédent
  const trendPercentage = previousValue > 0 ? ((currentValue - previousValue) / previousValue) * 100 : 0;
  const isPositiveTrend = trendPercentage >= 0;

  console.log(`Tendance: ${previousValue} → ${currentValue} = ${trendPercentage.toFixed(1)}%`);

  try {
    return (
      <div className="w-full h-full relative">
        {/* Indicateur de tendance - repositionné en bas à droite */}
        <div className="absolute bottom-1 right-1 z-20 flex items-center space-x-1 text-xs">
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium shadow-sm ${
            isPositiveTrend
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}>
            <span className="mr-1">{isPositiveTrend ? '↗' : '↘'}</span>
            {trendPercentage > 0 ? '+' : ''}{trendPercentage.toFixed(1)}%
          </span>
        </div>

        <ResponsiveContainer width="100%" height={height}>
          <LineChart
            data={chartData}
            margin={{
              top: height > 100 ? 28 : 16,
              right: height > 100 ? 20 : 10,
              left: height > 100 ? 45 : 35,
              bottom: height > 100 ? 25 : 20
            }}
          >
            <defs>
              <linearGradient id="peGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            
            {/* Grille de fond */}
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#E5E7EB"
              opacity={0.5}
            />

            <XAxis
              dataKey="month"
              axisLine={true}
              tickLine={true}
              tick={{ fontSize: 10, fill: '#374151', fontWeight: 500 }}
              interval={0}
              stroke="#9CA3AF"
            />

            <YAxis
              axisLine={true}
              tickLine={true}
              tick={{ fontSize: 9, fill: '#374151' }}
              tickFormatter={(value) => {
                if (value >= 1000) {
                  return `${Math.round(value / 1000)}k`;
                }
                return value.toString();
              }}
              stroke="#9CA3AF"
              width={35}
              domain={[(dataMin: number) => Math.floor(dataMin * 0.9), (dataMax: number) => Math.ceil(dataMax * 1.1)]}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Line
              type="monotone"
              dataKey="value"
              stroke="#8B5CF6"
              strokeWidth={3}
              dot={{
                fill: '#8B5CF6',
                strokeWidth: 2,
                stroke: '#fff',
                r: height > 100 ? 5 : 4
              }}
              activeDot={{
                r: height > 100 ? 8 : 6,
                stroke: '#8B5CF6',
                strokeWidth: 3,
                fill: '#fff'
              }}
              animationDuration={1500}
              connectNulls
            >
              {/* Labels sur les points */}
              <LabelList
                dataKey="value"
                position="top"
                offset={8}
                formatter={(label: any) => {
                  const value = typeof label === 'number' ? label : 0;
                  return value >= 1000 ? `${Math.round(value / 1000)}k` : value;
                }}
                style={{
                  fontSize: '9px',
                  fill: '#6B7280',
                  fontWeight: 'bold'
                }}
              />
            </Line>
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  } catch (error) {
    console.error('PublicEngagementTrendChart render error:', error);
    return (
      <div className="h-full flex items-center justify-center text-red-400 text-xs">
        <div className="text-center">
          <div>⚠️</div>
          <div className="mt-1">Erreur graphique</div>
        </div>
      </div>
    );
  }
};

export default PublicEngagementTrendChart;
