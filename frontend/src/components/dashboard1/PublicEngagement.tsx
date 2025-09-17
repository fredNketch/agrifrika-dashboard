import React from 'react';
import { DashboardCard } from '../shared';
import PublicEngagementTrendChart from './PublicEngagementTrendChart';
import type { PublicEngagementData } from '../../types';

interface PublicEngagementProps {
  data: PublicEngagementData | null;
  loading?: boolean;
}

const PublicEngagement: React.FC<PublicEngagementProps> = ({ data, loading = false }) => {
  if (!data && !loading) return null;
  
  // Calcul du pourcentage de score (exact au dixième près)
  const scorePercentage = data ? (data.score / 100) * 100 : 0;
  
  return (
    <DashboardCard
      title="Public Engagement"
      icon="👥"
      loading={loading}
      className="h-full flex flex-col"
    >
      {data && (
        <div className="h-full flex flex-col space-y-2">
          {/* Header avec score principal */}
          <div className="flex items-center justify-between bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-2 border border-purple-200">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">{scorePercentage.toFixed(1)}%</span>
              </div>
              <div>
                <div className="text-xs font-medium text-gray-600">Score d'engagement</div>
                <div className="text-sm font-bold text-gray-800">
                  {data.total_points.toLocaleString()} / {data.max_points.toLocaleString()} pts
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs text-gray-500">Dernière MAJ</div>
              <div className="text-xs font-medium text-gray-700">
                {new Date().toLocaleDateString('fr-FR')}
              </div>
            </div>
          </div>
          
          {/* Répartition par plateforme - Layout compact */}
          <div className="grid grid-cols-5 gap-1">
            {[
              { name: 'Facebook', value: data.sources.facebook, color: 'bg-blue-500', icon: '📱', bg: 'bg-blue-50' },
              { name: 'LinkedIn', value: data.sources.linkedin, color: 'bg-indigo-500', icon: '💼', bg: 'bg-indigo-50' },
              { name: 'Site Web', value: data.sources.website, color: 'bg-green-500', icon: '🌐', bg: 'bg-green-50' },
              { name: 'Newsletter', value: data.sources.newsletter, color: 'bg-yellow-500', icon: '📧', bg: 'bg-yellow-50' },
              { name: 'Événements', value: data.sources.events, color: 'bg-red-500', icon: '🎯', bg: 'bg-red-50' }
                    ].map((source, index) => (
              <div key={index} className={`${source.bg} rounded-md p-1 border border-gray-200 text-center`}>
                <div className={`w-2 h-2 rounded-full ${source.color} mx-auto mb-0.5`}></div>
                <div className="text-xs font-medium text-gray-700 mb-0.5">{source.name}</div>
                <div className="text-xs font-bold text-gray-800">{source.value.toLocaleString()}</div>
                      </div>
                    ))}
                  </div>

          {/* Métriques détaillées - Layout horizontal compact */}
          {data.detailed_metrics && (
            <div className="bg-white rounded-lg p-2 border border-gray-200 shadow-sm">
              <div className="text-xs font-bold text-gray-800 mb-1 flex items-center">
                <span className="mr-1">📊</span> Métriques Clés
              </div>
              <div className="grid grid-cols-4 gap-1">
                {[
                  { name: 'Likes', value: data.detailed_metrics.likes_reactions, icon: '👍', color: 'text-blue-600' },
                      { name: 'Partages', value: data.detailed_metrics.partages, icon: '🔄', color: 'text-green-600' },
                      { name: 'Commentaires', value: data.detailed_metrics.commentaires, icon: '💬', color: 'text-purple-600' },
                  { name: 'Abonnés', value: data.detailed_metrics.nouveaux_abonnes, icon: '➕', color: 'text-indigo-600' }
                ].map((metric, index) => (
                  <div key={index} className="text-center p-1 bg-gray-50 rounded-md">
                    <div className="text-sm mb-0.5">{metric.icon}</div>
                    <div className="text-xs font-medium text-gray-600 mb-0.5">{metric.name}</div>
                    <div className={`text-xs font-bold ${metric.color}`}>{metric.value.toLocaleString()}</div>
                      </div>
                    ))}
                </div>
              </div>
            )}
            
                      {/* Top contenus et tendance - Layout horizontal */}
            <div className="flex-1 grid grid-cols-2 gap-2">
              {/* Top contenus */}
              <div className="bg-white rounded-lg p-2 border border-gray-200 shadow-sm">
                <div className="text-xs font-bold text-gray-800 mb-1 flex items-center">
                  <span className="mr-1">🏆</span> Top Contenus
                </div>
                <div className="space-y-1">
                  {data.top_content && data.top_content.length > 0 ? (
                    data.top_content.slice(0, 2).map((content, index) => (
                      <div key={index} className="p-1 bg-gradient-to-r from-purple-50 to-purple-100 rounded-md border border-purple-200">
                        <div 
                          className="text-xs font-semibold text-gray-800 truncate mb-0.5 cursor-pointer hover:text-purple-600 transition-colors"
                          onClick={() => content.url && window.open(content.url, '_blank')}
                          title={content.url ? "Cliquer pour ouvrir le lien" : ""}
                        >
                          {content.title}
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-purple-600">{content.platform}</span>
                          <span className="text-xs font-bold text-purple-700">
                            {content.vues ? `${content.vues.toLocaleString()} vues` : '0 vues'}
                          </span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-2 text-center text-gray-400 text-xs">
                      Aucun contenu disponible
                    </div>
                  )}
                </div>
              </div>
              
                         {/* Tendance mensuelle */}
             <div className="bg-white rounded-lg p-2 border border-gray-200 shadow-sm">
               <div className="text-xs font-bold text-gray-800 mb-1 flex items-center">
                 <span className="mr-1">📈</span> Tendance
               </div>
               <div className="h-24 w-full">
                 {data.monthly_trend && data.monthly_trend.length > 0 ? (
                   <PublicEngagementTrendChart
                     data={data.monthly_trend}
                     height={90}
                   />
                 ) : (
                   <div className="h-full flex items-center justify-center text-gray-400 text-xs">
                     <div className="text-center">
                       <div className="animate-pulse text-lg">📊</div>
                       <div className="mt-1">Aucune tendance disponible</div>
                     </div>
                   </div>
                 )}
               </div>
             </div>
            </div>
            
          {/* Métriques supplémentaires - Layout compact */}
          {data.detailed_metrics && (
            <div className="bg-white rounded-lg p-2 border border-gray-200 shadow-sm">
              <div className="grid grid-cols-3 gap-1">
                {[
                  { name: 'App Téléchargée', value: data.detailed_metrics.telechargement_app, icon: '📱', color: 'text-teal-600' },
                  { name: 'Mentions Médias', value: data.detailed_metrics.mention_medias, icon: '📺', color: 'text-red-600' },
                  { name: 'Recherches', value: data.detailed_metrics.apparition_recherches, icon: '🔍', color: 'text-amber-600' }
                ].map((metric, index) => (
                  <div key={index} className="text-center p-1 bg-gray-50 rounded-md">
                    <div className="text-xs mb-0.5">{metric.icon}</div>
                    <div className="text-xs font-medium text-gray-600 mb-0.5">{metric.name}</div>
                    <div className={`text-xs font-bold ${metric.color}`}>{metric.value.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </DashboardCard>
  );
};

export default PublicEngagement;