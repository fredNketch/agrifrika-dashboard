import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AnimatedCard from '../ui/AnimatedCard';
import type { ActionPlanItem } from '../../types';

interface ActionPlanProps {
  className?: string;
}

const ActionPlan: React.FC<ActionPlanProps> = ({ className = '' }) => {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const [data, setData] = useState<ActionPlanItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchActionPlan();
    const interval = setInterval(fetchActionPlan, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchActionPlan = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://dashboard.agrifrika.com/api/v1/dashboard2/action-plan', {
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

  // Utilise les vraies données ActionPlan depuis Basecamp ou fallback
  const calendarEvents = data?.map(item => ({
    date: item.due_date ? new Date(item.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'TBD',
    day: item.due_date ? new Date(item.due_date).toLocaleDateString('en-US', { weekday: 'short' }) : 'TBD',
    title: item.title,
    time: item.due_date ? new Date(item.due_date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) : 'À définir',
    type: item.priority === 'haute' ? 'important' : item.priority === 'moyenne' ? 'meeting' : 'planning',
    participants: item.assigned_to ? [item.assigned_to] : ['Non assigné'],
    status: item.status,
    category: item.category
  })) || [];

  const getEventColor = (type: string) => {
    switch (type) {
      case 'important': return { bg: 'bg-red-100 dark:bg-red-900/30', border: 'border-red-300 dark:border-red-700', text: 'text-red-700 dark:text-red-300' };
      case 'meeting': return { bg: 'bg-blue-100 dark:bg-blue-900/30', border: 'border-blue-300 dark:border-blue-700', text: 'text-blue-700 dark:text-blue-300' };
      case 'review': return { bg: 'bg-purple-100 dark:bg-purple-900/30', border: 'border-purple-300 dark:border-purple-700', text: 'text-purple-700 dark:text-purple-300' };
      case 'technical': return { bg: 'bg-green-100 dark:bg-green-900/30', border: 'border-green-300 dark:border-green-700', text: 'text-green-700 dark:text-green-300' };
      case 'planning': return { bg: 'bg-orange-100 dark:bg-orange-900/30', border: 'border-orange-300 dark:border-orange-700', text: 'text-orange-700 dark:text-orange-300' };
      case 'product': return { bg: 'bg-indigo-100 dark:bg-indigo-900/30', border: 'border-indigo-300 dark:border-indigo-700', text: 'text-indigo-700 dark:text-indigo-300' };
      default: return { bg: 'bg-gray-100 dark:bg-gray-800', border: 'border-gray-300 dark:border-gray-600', text: 'text-gray-700 dark:text-gray-300' };
    }
  };

  // Auto-scroll pour voir tous les événements
  useEffect(() => {
    if (!isAutoScrolling || calendarEvents.length <= 4) return;

    const interval = setInterval(() => {
      setScrollPosition(prev => {
        const maxScroll = Math.max(0, calendarEvents.length - 4);
        return prev >= maxScroll ? 0 : prev + 1;
      });
    }, 20000); // Change toutes les 10 secondes

    return () => clearInterval(interval);
  }, [isAutoScrolling, calendarEvents.length]);


  return (
    <AnimatedCard
      title={`Plan d'action (${data?.length || 0} tâches)`}
      icon="📅"
      loading={loading}
      className={`h-full ${className}`}
    >
      <div className="space-y-3 h-full flex flex-col">
        {/* Header style Basecamp */}
        <div className="bg-gray-100 dark:bg-gray-800 p-2 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-blue-600 dark:text-blue-400 font-semibold text-sm">📅 Cette semaine</span>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {calendarEvents.length} événements
            </div>
          </div>
        </div>

        {/* Liste des événements avec scroll automatique */}
        <div 
          className="flex-1 overflow-hidden"
          onMouseEnter={() => setIsAutoScrolling(false)}
          onMouseLeave={() => setIsAutoScrolling(true)}
        >
          <div className="space-y-2">
            {calendarEvents.length > 0 ? calendarEvents
              .slice(scrollPosition, scrollPosition + 4)
              .map((event, index) => {
                const colors = getEventColor(event.type);
                return (
                  <motion.div
                    key={`${event.title}-${scrollPosition}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`${colors.bg} ${colors.border} border rounded-lg p-3 hover:shadow-md transition-all duration-300`}
                  >
                    {/* Date et jour */}
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 text-center">
                        <div className={`${colors.text} font-bold text-sm`}>
                          {event.date}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 uppercase font-medium">
                          {event.day}
                        </div>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        {/* Titre de l'événement */}
                        <div className={`${colors.text} font-semibold text-sm mb-1 truncate`}>
                          {event.title}
                        </div>
                        
                        {/* Heure */}
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                          🕒 {event.time}
                        </div>
                        
                        {/* Participants */}
                        <div className="flex flex-wrap gap-1">
                          {event.participants.slice(0, 2).map((participant, idx) => (
                            <span 
                              key={idx}
                              className="inline-block bg-white dark:bg-gray-700 px-2 py-0.5 rounded-full text-xs border border-gray-200 dark:border-gray-600"
                            >
                              👤 {participant}
                            </span>
                          ))}
                          {event.participants.length > 2 && (
                            <span className="inline-block bg-gray-200 dark:bg-gray-600 px-2 py-0.5 rounded-full text-xs">
                              +{event.participants.length - 2}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              }) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center text-gray-500 dark:text-gray-400">
                    <div className="text-sm mb-2">📅</div>
                    <div className="text-xs">
                      {loading ? 'Chargement...' : 'Aucune donnée disponible'}
                    </div>
                  </div>
                </div>
              )
            }
          </div>
        </div>

        {/* Indicateur de scroll */}
        {calendarEvents.length > 4 && (
          <div className="flex justify-center space-x-1 flex-shrink-0">
            {Array.from({ length: Math.ceil(calendarEvents.length / 4) }).map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  Math.floor(scrollPosition / 4) === index ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>
        )}

        {/* Statistiques en bas style Basecamp */}
        <div className="grid grid-cols-3 gap-2 text-center flex-shrink-0">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded border border-blue-200 dark:border-blue-700">
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {calendarEvents.filter(e => e.type === 'important' || e.type === 'meeting').length}
            </div>
            <div className="text-xs text-blue-600 dark:text-blue-400">Meetings</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-2 rounded border border-green-200 dark:border-green-700">
            <div className="text-lg font-bold text-green-600 dark:text-green-400">
              {calendarEvents.filter(e => e.type === 'review' || e.type === 'planning').length}
            </div>
            <div className="text-xs text-green-600 dark:text-green-400">Reviews</div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-2 rounded border border-purple-200 dark:border-purple-700">
            <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
              {calendarEvents.filter(e => e.type === 'technical' || e.type === 'product').length}
            </div>
            <div className="text-xs text-purple-600 dark:text-purple-400">Dev</div>
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
};

export default ActionPlan;