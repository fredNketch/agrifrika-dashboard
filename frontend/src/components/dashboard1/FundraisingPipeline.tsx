import React from 'react';
import AnimatedCard from '../ui/AnimatedCard';
import { AnimatedChart } from '../shared';
import FundraisingTrendChart from './FundraisingTrendChart';
import type { FundraisingPipelineData } from '../../types';

interface FundraisingPipelineProps {
  data: FundraisingPipelineData | null;
  loading?: boolean;
}

const FundraisingPipeline: React.FC<FundraisingPipelineProps> = ({ data, loading = false }) => {
  if (!data && !loading) return null;
  
  const progressPercentage = data ? (data.score / 100) * 100 : 0;
  
  return (
    <AnimatedCard 
      title="Fundraising Pipeline"
      icon="📊"
      loading={loading}
      premium
      className="h-full flex flex-col"
    >
      {data && (
        <div className="h-full flex flex-col space-y-3">
          {/* Header avec score principal */}
          <div className="flex items-center justify-between bg-gradient-to-r from-red-50 to-pink-50 rounded-lg p-3 border border-red-200">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-600 rounded-full flex items-center justify-center">
                <span className="text-white text-lg font-bold">{progressPercentage.toFixed(1)}%</span>
              </div>
              <div>
                <div className="text-sm font-medium text-gray-600">Progression Financement</div>
                <div className="text-lg font-bold text-gray-800">
                  {data.total_points.toLocaleString()} / {data.max_points.toLocaleString()} pts
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Dernière MAJ</div>
              <div className="text-sm font-medium text-gray-700">
                {new Date().toLocaleDateString('fr-FR')}
              </div>
            </div>
          </div>

          {/* Répartition par catégorie - Layout compact */}
          <div className="grid grid-cols-4 gap-2">
            {[
              { name: 'Concours', value: data.categories.concours, color: 'bg-yellow-500', icon: '🏆', bg: 'bg-yellow-50' },
              { name: 'Subventions', value: data.categories.subventions, color: 'bg-green-500', icon: '🏦', bg: 'bg-green-50' },
              { name: 'Investisseurs', value: data.categories.investisseurs, color: 'bg-blue-500', icon: '💼', bg: 'bg-blue-50' },
              { name: 'Activités', value: data.categories.activités, color: 'bg-purple-500', icon: '🎯', bg: 'bg-purple-50' }
            ].map((category, index) => (
              <div key={index} className={`${category.bg} rounded-lg p-2 border border-gray-200 text-center`}>
                <div className={`w-3 h-3 rounded-full ${category.color} mx-auto mb-1`}></div>
                <div className="text-xs font-medium text-gray-700 mb-1">{category.name}</div>
                <div className="text-sm font-bold text-gray-800">{category.value.toLocaleString()}</div>
              </div>
            ))}
          </div>

          {/* Échéances et tendance - Layout horizontal */}
          <div className="flex-1 grid grid-cols-2 gap-3">
            {/* Prochaines échéances */}
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
              <div className="text-xs font-bold text-gray-800 mb-2 flex items-center">
                <span className="mr-1">📅</span> Prochaines Échéances
              </div>
              <div className="space-y-2">
                {data.upcoming_deadlines && data.upcoming_deadlines.length > 0 ? (
                  data.upcoming_deadlines.slice(0, 2).map((deadline, index) => {
                    const typeColors = {
                      concours: 'bg-yellow-50 border-yellow-200 text-yellow-800',
                      subvention: 'bg-green-50 border-green-200 text-green-800',
                      investisseur: 'bg-blue-50 border-blue-200 text-blue-800'
                    };
                    
                    return (
                      <div key={index} className={`p-2 rounded-md border ${typeColors[deadline.type]}`}>
                        <div className="text-xs font-semibold truncate mb-1">
                          {deadline.title}
                        </div>
                        <div className="text-xs font-medium">
                          {new Date(deadline.date).toLocaleDateString('fr-FR', { 
                            day: 'numeric', 
                            month: 'short' 
                          })}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="p-2 text-center text-gray-400 text-xs">
                    Aucune échéance
                  </div>
                )}
              </div>
            </div>
            
            {/* Tendance des engagements - Design ultra-moderne */}
            <div className="bg-gradient-to-br from-white via-blue-50/20 to-purple-50/20 rounded-2xl p-6 border border-blue-100/50 shadow-2xl backdrop-blur-sm relative overflow-hidden">
              {/* Effet de brillance en arrière-plan */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5 rounded-2xl"></div>
              
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                      <span className="text-white text-lg">📈</span>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-gray-800">Tendance</div>
                      <div className="text-sm text-gray-600 font-medium">Évolution du fundraising</div>
                    </div>
                  </div>
                  <div className="text-right bg-white/80 backdrop-blur-sm rounded-xl px-4 py-3 border border-blue-200/50 shadow-lg">
                    <div className="text-xs text-gray-500 font-medium">Dernière période</div>
                    <div className="text-lg font-bold text-gray-800">
                      {data.trends_data && data.trends_data.length > 0 
                        ? `+${data.trends_data[data.trends_data.length - 1]?.activity_points || 0} pts`
                        : 'N/A'
                      }
                    </div>
                  </div>
              </div>
                
                <div className="h-40">
                  {data.trends_data && data.trends_data.length > 0 ? (
                    <FundraisingTrendChart 
                      data={data.trends_data}
                      height={160}
                    />
                  ) : data.progress_chart && data.progress_chart.length > 0 ? (
                  <AnimatedChart 
                    type="line"
                    data={data.progress_chart.slice(-3).map(item => ({
                      name: item.month,
                      value: item.amount
                    }))}
                      height={160}
                      colors={['#3B82F6']}
                      gradient={true}
                    animated={true}
                    config={{
                      xKey: 'name',
                      yKey: 'value'
                    }}
                  />
                ) : (
                    <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                      <div className="text-center">
                        <div className="animate-pulse text-3xl">📊</div>
                        <div className="mt-3 font-medium">Chargement des tendances...</div>
                      </div>
                  </div>
                )}
                </div>
              </div>
            </div>
          </div>

          {/* Résumé des objectifs */}
          <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm">
            <div className="text-center">
              <div className="text-sm font-bold text-red-600 mb-1">
                Objectif: {data.total_points.toLocaleString()} / {data.max_points.toLocaleString()} points
              </div>
              <div className="text-xs text-gray-500">
                Progression: {((data.total_points / data.max_points) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}
    </AnimatedCard>
  );
};

export default FundraisingPipeline;