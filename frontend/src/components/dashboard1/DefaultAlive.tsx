import React from 'react';
import { DashboardCard, CircularGauge } from '../shared';
import type { DefaultAliveData } from '../../types';

interface DefaultAliveProps {
  data: DefaultAliveData | null;
  loading?: boolean;
}

const DefaultAlive: React.FC<DefaultAliveProps> = ({ data, loading = false }) => {
  if (!data && !loading) return null;
  
  // Détermination de la couleur selon les mois restants
  const getHealthColor = (months: number) => {
    if (months > 6) return 'green';
    if (months > 3) return 'orange';
    return 'red';
  };
  
  const healthColor = data ? getHealthColor(data.default_alive_practical) : 'green';
  
  return (
    <DashboardCard
      title="Default Alive"
      icon="💰"
      loading={loading}
      className="h-full flex flex-col"
    >
      {data && (
        <div className="h-full flex flex-col justify-between space-y-2">
          {/* Zone principale - Gauge et statut */}
          <div className="flex-1 flex flex-col items-center justify-center space-y-3">
            {/* Gauge circulaire principale */}
            <CircularGauge 
              value={data.default_alive_practical}
              maxValue={12}
              size="md"
              colors={
                healthColor === 'green' ? ['#10B981', '#34D399', '#6EE7B7'] :
                healthColor === 'orange' ? ['#F59E0B', '#FBBF24', '#FCD34D'] :
                ['#EF4444', '#F87171', '#FCA5A5']
              }
              label="mois restants"
              unit=""
              animated={true}
            />
            
            {/* Badge de statut */}
            <div className={`inline-flex items-center px-4 py-1 rounded-full text-sm font-bold shadow-md border border-white ${
              healthColor === 'green' ? 'bg-green-100 text-green-800' :
              healthColor === 'orange' ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            }`}>
              <span className="mr-1 text-base">
                {healthColor === 'green' ? '✅' : healthColor === 'orange' ? '⚠️' : '🚨'}
              </span>
              <span>
                {healthColor === 'green' ? 'Santé financière saine' :
                 healthColor === 'orange' ? 'Attention requise' :
                 'Situation critique'}
              </span>
            </div>
          </div>
          
          {/* Zone inférieure - Métriques ultra-compactes */}
          <div className="flex-shrink-0 space-y-2">
            {/* Comparaison Pratique vs Théorique */}
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg shadow-sm border border-gray-200">
                <div className="text-2xl font-bold text-gray-800">
                  {data.default_alive_practical.toFixed(1)}
                </div>
                <div className="text-xs font-semibold text-gray-600">Pratique</div>
              </div>
              <div className="text-center p-2 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200">
                <div className="text-2xl font-bold text-blue-800">
                  {data.default_alive_theoretical.toFixed(1)}
                </div>
                <div className="text-xs font-semibold text-blue-600">Théorique</div>
              </div>
            </div>
            
            {/* Métriques financières */}
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center p-1 bg-gradient-to-br from-green-50 to-green-100 rounded-md shadow-sm border border-green-200">
                <div className="text-sm font-bold text-green-700">
                  {data.cash_available.toLocaleString()}$
                </div>
                <div className="text-xs font-medium text-green-600">Cash disponible</div>
              </div>
              
              <div className="text-center p-1 bg-gradient-to-br from-blue-50 to-blue-100 rounded-md shadow-sm border border-blue-200">
                <div className="text-sm font-bold text-blue-700">
                  {data.promised_funds.toLocaleString()}$
                </div>
                <div className="text-xs font-medium text-blue-600">Fonds promis</div>
              </div>
              
              <div className="text-center p-1 bg-gradient-to-br from-red-50 to-red-100 rounded-md shadow-sm border border-red-200">
                <div className="text-sm font-bold text-red-700">
                  {data.monthly_charges.toLocaleString()}$
                </div>
                <div className="text-xs font-medium text-red-600">Charges/mois</div>
              </div>
            </div>
            
            {/* Tendance et mise à jour */}
            <div className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-2 shadow-sm border border-gray-200">
              <div className="text-center">
                <div className="text-xs font-medium text-gray-600">Tendance</div>
                <div className={`flex items-center text-sm font-bold ${
                  data.trend_percentage > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  <span className="mr-1 text-base">
                    {data.trend_percentage > 0 ? '↗️' : '↘️'}
                  </span>
                  <span>{Math.abs(data.trend_percentage).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-xs font-medium text-gray-600">Mise à jour</div>
                <div className="text-xs font-semibold text-gray-800">
                  {new Date(data.last_updated).toLocaleDateString('fr-FR')}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardCard>
  );
};

export default DefaultAlive;