import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AnimatedCard from '../ui/AnimatedCard';
import type { WeeklyPlanningData } from '../../types';

interface WeeklyPlanningProps {
  className?: string;
}

const WeeklyPlanning: React.FC<WeeklyPlanningProps> = ({ className = '' }) => {
  const [data, setData] = useState<WeeklyPlanningData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentRowIndex, setCurrentRowIndex] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchWeeklyPlanning();
    const interval = setInterval(fetchWeeklyPlanning, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);



  const fetchWeeklyPlanning = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://192.168.1.45:8000/api/v1/dashboard2/weekly-planning', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'API call failed');
      }

      setData(result.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion à l\'API');
    } finally {
      setLoading(false);
    }
  };

  // Structure exacte du Google Sheet - lignes uniques (pas de doublons)
  const getAllGoogleSheetRows = () => {
    if (!data?.daily_schedule) return [];
    
    const uniqueRows = [];
    const seenTasks = new Set();
    
    // Récupérer TOUTES les tâches de TOUS les jours mais éviter les doublons
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    
    days.forEach((day) => {
      const daySchedule = data.daily_schedule[day];
      if (daySchedule?.tasks) {
        daySchedule.tasks.forEach(task => {
          // Créer une clé unique pour éviter les doublons
          const taskKey = `${task.assigned_to}-${task.title}-${task.time}`;
          
          if (!seenTasks.has(taskKey)) {
            seenTasks.add(taskKey);
            uniqueRows.push({
              collaborateur: task.assigned_to || '',
              objectifs: task.objectives || '',
              taches: task.title || '',
              priorite: task.priority_display || '',  // Respecter les cellules vides
              dateLimite: task.time || '',
              statut: task.status || '',  // Respecter les cellules vides
              commentaires: task.comments || ''
            });
          }
        });
      }
    });
    
    return uniqueRows;
  };

  const googleSheetRows = getAllGoogleSheetRows();

  // Auto-scroll vertical doux
  useEffect(() => {
    if (!isAutoScrolling || !data?.daily_schedule || googleSheetRows.length === 0) return;

    const interval = setInterval(() => {
      setCurrentRowIndex(prev => {
        const nextIndex = (prev + 1) % googleSheetRows.length;
        
        // Scroll vers la ligne actuelle
        if (scrollContainerRef.current) {
          const container = scrollContainerRef.current;
          const rowHeight = 120; // hauteur approximative d'une ligne (h-28 + space-y-2)
          const scrollTop = nextIndex * rowHeight;
          
          container.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
        }
        
        return nextIndex;
      });
    }, 6000); // Change toutes les 6 secondes

    return () => clearInterval(interval);
  }, [isAutoScrolling, data?.daily_schedule, googleSheetRows.length]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'en cours': return { bg: 'bg-gradient-to-r from-blue-500 to-blue-600', text: 'text-white', border: 'border-blue-400' };
      case 'à faire': return { bg: 'bg-gradient-to-r from-orange-500 to-orange-600', text: 'text-white', border: 'border-orange-400' };
      case 'en attente': return { bg: 'bg-gradient-to-r from-gray-500 to-gray-600', text: 'text-white', border: 'border-gray-400' };
      case 'terminé': return { bg: 'bg-gradient-to-r from-emerald-500 to-emerald-600', text: 'text-white', border: 'border-emerald-400' };
      default: return { bg: 'bg-gradient-to-r from-gray-500 to-gray-600', text: 'text-white', border: 'border-gray-400' };
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-gradient-to-r from-red-500 to-red-600';
      case 'medium': return 'bg-gradient-to-r from-orange-500 to-orange-600';
      case 'low': return 'bg-gradient-to-r from-emerald-500 to-emerald-600';
      default: return 'bg-gradient-to-r from-gray-500 to-gray-600';
    }
  };

  return (
    <AnimatedCard
      title={`Planning W${data?.week_number || 34} (${data?.completion_stats?.completed || 0}/${data?.completion_stats?.total || 0})`}
      icon="📋"
      loading={loading}
      className={`h-full ${className}`}
    >
      <div 
        className="space-y-4 h-full flex flex-col"
        onMouseEnter={() => setIsAutoScrolling(false)}
        onMouseLeave={() => setIsAutoScrolling(true)}
      >
        {/* En-tête moderne avec gradient vert du logo */}
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl overflow-hidden flex-shrink-0 shadow-lg">
          <div className="grid grid-cols-7 text-center font-bold text-sm text-white" style={{ gridTemplateColumns: '1fr 1fr 1fr 80px 80px 80px 1fr' }}>
            <div className="py-3 px-2 border-r border-white/20">👤 Collaborateur</div>
            <div className="py-3 px-2 border-r border-white/20">🎯 Objectifs</div>
            <div className="py-3 px-2 border-r border-white/20">📝 Tâches</div>
            <div className="py-3 px-2 border-r border-white/20">⚡ Priorité</div>
            <div className="py-3 px-2 border-r border-white/20">📅 Date</div>
            <div className="py-3 px-2 border-r border-white/20">🔄 Statut</div>
            <div className="py-3 px-2">💬 Commentaires</div>
          </div>
        </div>

        {/* Tableau avec auto-scroll doux */}
        <div ref={scrollContainerRef} className="flex-1 overflow-y-auto">
          <div className="space-y-2">
            {googleSheetRows.length > 0 ? googleSheetRows.map((row, index) => {
                const statusInfo = getStatusColor(row.statut);
                return (
                  <motion.div
                    key={`${row.collaborateur}-${row.taches}-${index}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="grid grid-cols-7 bg-white dark:bg-gray-800 rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300 min-h-0 h-28 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                    style={{ gridTemplateColumns: '1fr 1fr 1fr 80px 80px 80px 1fr' }}
                  >
                    {/* Collaborateur */}
                    <div className="py-3 px-3 border-r border-gray-200 dark:border-gray-700 flex items-center">
                      <div className="text-sm font-bold text-gray-800 dark:text-gray-100 truncate">
                        {row.collaborateur || '-'}
                      </div>
                    </div>
                    
                    {/* Objectifs de la semaine */}
                    <div className="py-3 px-3 border-r border-gray-200 dark:border-gray-700">
                      <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed overflow-y-auto overflow-x-auto max-h-20 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 w-full h-full">
                        {row.objectifs || '-'}
                      </div>
                    </div>
                    
                    {/* Tâches assignées */}
                    <div className="py-3 px-3 border-r border-gray-200 dark:border-gray-700">
                      <div className="text-sm text-gray-800 dark:text-gray-100 leading-relaxed overflow-y-auto overflow-x-auto max-h-20 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 w-full h-full font-medium">
                        {row.taches || '-'}
                      </div>
                    </div>
                    
                    {/* Priorité */}
                    <div className="py-3 px-2 border-r border-gray-200 dark:border-gray-700 text-center flex items-center justify-center">
                      {row.priorite ? (
                        <div className={`w-16 h-7 rounded-full text-xs font-bold shadow-lg flex items-center justify-center ${
                          row.priorite === 'Haute' ? 'bg-gradient-to-r from-red-500 to-red-600 text-white' :
                          row.priorite === 'Moyenne' ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white' :
                          'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white'
                        }`}>
                          {row.priorite}
                        </div>
                      ) : (
                        <div className="text-sm text-gray-400">-</div>
                      )}
                    </div>
                    
                    {/* Date limite */}
                    <div className="py-3 px-2 border-r border-gray-200 dark:border-gray-700 text-center flex items-center justify-center">
                      <div className="text-sm font-bold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-lg">
                        {row.dateLimite || '-'}
                      </div>
                    </div>
                    
                    {/* Statut */}
                    <div className="py-3 px-2 border-r border-gray-200 dark:border-gray-700 text-center flex items-center justify-center">
                      {row.statut ? (
                        <span className={`w-16 h-7 rounded-full text-xs font-bold shadow-lg flex items-center justify-center ${statusInfo.bg}`}>
                          {row.statut}
                        </span>
                      ) : (
                        <div className="text-sm text-gray-400">-</div>
                      )}
                    </div>
                    
                    {/* Commentaires/Notes */}
                    <div className="py-3 px-3">
                      <div className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed overflow-y-auto overflow-x-auto max-h-20 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 w-full h-full">
                        {row.commentaires || '-'}
                      </div>
                    </div>
                  </motion.div>
                );
              }) : (
                <motion.div 
                  className="flex-1 flex items-center justify-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="text-center text-gray-500">
                    <div className="text-4xl mb-4">📋</div>
                    <div className="text-lg font-medium mb-2">Aucune donnée disponible</div>
                    <div className="text-sm">Vérifiez la connexion à l'API</div>
                  </div>
                </motion.div>
              )
            }
          </div>
        </div>



        {/* Résumé des priorités - design moderne */}
        <div className="grid grid-cols-3 gap-3 text-center flex-shrink-0">
          <motion.div 
            className="bg-gradient-to-r from-red-500 to-red-600 py-3 px-3 rounded-xl shadow-lg border border-red-400"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <div className="text-xl font-bold text-white">
              {googleSheetRows.filter(r => r.priorite === 'Haute').length}
            </div>
            <div className="text-sm text-red-100 font-medium">Haute</div>
          </motion.div>
          
          <motion.div 
            className="bg-gradient-to-r from-orange-500 to-orange-600 py-3 px-3 rounded-xl shadow-lg border border-orange-400"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <div className="text-xl font-bold text-white">
              {googleSheetRows.filter(r => r.priorite === 'Moyenne').length}
            </div>
            <div className="text-sm text-orange-100 font-medium">Moyenne</div>
          </motion.div>
          
          <motion.div 
            className="bg-gradient-to-r from-emerald-500 to-emerald-600 py-3 px-3 rounded-xl shadow-lg border border-emerald-400"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
          >
            <div className="text-xl font-bold text-white">
              {googleSheetRows.filter(r => r.statut === 'Terminé').length}
            </div>
            <div className="text-sm text-emerald-100 font-medium">Terminé</div>
          </motion.div>
        </div>
      </div>
    </AnimatedCard>
  );
};

export default WeeklyPlanning;