import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AnimatedCard from '../ui/AnimatedCard';
import type { BasecampData } from '../../types';

interface BasecampTodosProps {
  data: BasecampData | null;
  loading?: boolean;
}

const BasecampTodos: React.FC<BasecampTodosProps> = ({ data, loading = false }) => {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);

  // Utilise les vraies données Basecamp ou fallback
  const basecampTodos = data?.todos || [];
  
  // Groupe les todos par projet
  const todosCategories = basecampTodos.reduce((categories: any[], todo) => {
    let category = categories.find(cat => cat.title === todo.project);
    
    if (!category) {
      category = {
        title: todo.project || 'Sans projet',
        description: '',
        todos: []
      };
      categories.push(category);
    }
    
    category.todos.push({
      title: todo.title,
      assignee: todo.assigned_to || 'Non assigné',
      dueDate: todo.due_date ? new Date(todo.due_date).toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      }) : 'Pas de deadline',
      // Harmoniser les statuts: backend envoie "termine" (sans accent), certains types/frontend utilisent "terminé"
      status: (todo.status === 'termine' || todo.status === 'terminé' || todo.status === 'completed') ? 'completed' : 'active'
    });
    
    return categories;
  }, []);

  // Pas de fallback - on affiche seulement les vraies données

  const getProgressColor = (completed: number, total: number) => {
    const percentage = (completed / total) * 100;
    if (percentage === 0) return 'text-gray-500';
    if (percentage < 50) return 'text-red-600';
    if (percentage < 100) return 'text-orange-600';
    return 'text-green-600';
  };

  const getStatusIcon = (status: string) => {
    return status === 'completed' ? '✅' : '⬜';
  };

  // Auto-scroll pour voir toutes les catégories
  useEffect(() => {
    if (!isAutoScrolling || todosCategories.length <= 2) return;

    const interval = setInterval(() => {
      setScrollPosition(prev => {
        const maxScroll = Math.max(0, todosCategories.length - 2);
        return prev >= maxScroll ? 0 : prev + 1;
      });
    }, 15000); // Change toutes les 12 secondes

    return () => clearInterval(interval);
  }, [isAutoScrolling, todosCategories.length]);


  return (
    <AnimatedCard
      title={`To-dos ${data?.completed_today || 0} terminés aujourd'hui`}
      icon="✅"
      loading={loading}
      className="h-full"
    >
      <div className="space-y-3 h-full flex flex-col">
        {/* Header style Basecamp */}
        <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-2 rounded-lg border border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button className="bg-green-600 text-white px-3 py-1 rounded text-xs font-medium hover:bg-green-700 transition-colors">
            ➕ New list
          </button>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-600 dark:text-gray-400">View as...</span>
            <button className="text-xs text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">⋯</button>
          </div>
        </div>

        {/* Liste des catégories avec scroll automatique */}
        <div 
          className="flex-1 overflow-hidden"
          onMouseEnter={() => setIsAutoScrolling(false)}
          onMouseLeave={() => setIsAutoScrolling(true)}
        >
          <div className="space-y-3">
            {todosCategories
              .slice(scrollPosition, scrollPosition + 2)
              .map((category, index) => {
                const completedCount = category.todos.filter(t => t.status === 'completed').length;
                const totalCount = category.todos.length;
                
                return (
                  <motion.div
                    key={`${category.title}-${scrollPosition}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.2 }}
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 shadow-sm hover:shadow-md transition-all duration-300"
                  >
                    {/* En-tête de catégorie */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center">
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        </div>
                        <h3 className="font-semibold text-sm text-blue-600 dark:text-blue-400 underline">
                          {category.title}
                        </h3>
                      </div>
                      <div className={`text-xs font-medium ${getProgressColor(completedCount, totalCount)}`}>
                        {completedCount}/{totalCount} completed
                      </div>
                    </div>

                    {/* Description si disponible */}
                    {category.description && (
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 line-clamp-1">
                        {category.description}
                      </p>
                    )}

                    {/* Lista des todos (maximum 2 visibles) */}
                    <div className="space-y-2">
                      {category.todos.slice(0, 2).map((todo, todoIndex) => (
                        <div 
                          key={todoIndex}
                          className="flex items-start space-x-2 p-2 bg-gray-50 dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                        >
                          <div className="text-sm mt-0.5">
                            {getStatusIcon(todo.status)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className={`text-xs font-medium leading-tight mb-1 ${
                              todo.status === 'completed' 
                                ? 'line-through text-gray-500 dark:text-gray-400'
                                : 'text-gray-800 dark:text-gray-100'
                            }`}>
                              {todo.title.length > 60 ? `${todo.title.substring(0, 60)}...` : todo.title}
                            </div>
                            
                            {/* Assigné et date */}
                            <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                              {todo.assignee && (
                                <div className="flex items-center space-x-1">
                                  <span>👤</span>
                                  <span>{todo.assignee.split(',').length > 1 ? `${todo.assignee.split(',')[0]}...` : todo.assignee}</span>
                                </div>
                              )}
                              {todo.dueDate && (
                                <div className="flex items-center space-x-1">
                                  <span>📅</span>
                                  <span className="bg-orange-100 dark:bg-orange-900/30 px-1 rounded text-orange-700 dark:text-orange-300">
                                    {todo.dueDate}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                      
                      {category.todos.length > 2 && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-1">
                          ... et {category.todos.length - 2} autres tâches
                        </div>
                      )}
                    </div>

                    {/* Bouton Add a to-do */}
                    <button className="w-full text-left text-xs text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 mt-3 py-1">
                      + Add a to-do
                    </button>
                  </motion.div>
                );
              })
            }
          </div>
        </div>

        {/* Indicateur de scroll */}
        {todosCategories.length > 2 && (
          <div className="flex justify-center space-x-1 flex-shrink-0">
            {Array.from({ length: Math.ceil(todosCategories.length / 2) }).map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  Math.floor(scrollPosition / 2) === index ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>
        )}

        {/* Statistiques globales */}
        <div className="grid grid-cols-3 gap-2 text-center flex-shrink-0">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded border border-blue-200 dark:border-blue-700">
            <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {todosCategories.length}
            </div>
            <div className="text-xs text-blue-600 dark:text-blue-400">Listes</div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-2 rounded border border-orange-200 dark:border-orange-700">
            <div className="text-lg font-bold text-orange-600 dark:text-orange-400">
              {todosCategories.reduce((acc, cat) => acc + cat.todos.filter(t => t.status === 'active').length, 0)}
            </div>
            <div className="text-xs text-orange-600 dark:text-orange-400">Actives</div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-2 rounded border border-green-200 dark:border-green-700">
            <div className="text-lg font-bold text-green-600 dark:text-green-400">
              {todosCategories.reduce((acc, cat) => acc + cat.todos.filter(t => t.status === 'completed').length, 0)}
            </div>
            <div className="text-xs text-green-600 dark:text-green-400">Terminées</div>
          </div>
        </div>
      </div>
    </AnimatedCard>
  );
};

export default BasecampTodos;