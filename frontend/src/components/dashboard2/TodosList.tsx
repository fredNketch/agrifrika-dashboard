import React, { useState, useEffect, useRef } from 'react';
import { 
  CheckCircleIcon, 
  ClockIcon, 
  UserIcon, 
  CalendarIcon, 
  ExclamationTriangleIcon, 
  FunnelIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import DashboardCard from '../shared/DashboardCard';

// Types locaux pour éviter les problèmes d'import
interface TodoItem {
  id: string;
  title: string;
  status: string;
  assigned_to?: string;
  due_date?: string;
  project?: string;
  category?: string;
}

interface TodosByCategory {
  category: string;
  todos: TodoItem[];
  total_count: number;
  pending_count: number;
  completed_count: number;
}

interface TodosData {
  categories: TodosByCategory[];
  global_stats: {
    total: number;
    pending: number;
    completed: number;
    in_progress: number;
  };
  urgent_todos: TodoItem[];
  last_updated: string;
}

interface TodosListProps {
  className?: string;
}

export const TodosList: React.FC<TodosListProps> = ({ className = '' }) => {
  const [todosData, setTodosData] = useState<TodosData | null>(null);
  const [currentCategoryIndex, setCurrentCategoryIndex] = useState<number>(0);
  const [currentRowIndex, setCurrentRowIndex] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchTodos();
    const interval = setInterval(fetchTodos, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  // Rotation automatique entre les catégories avec temps adaptatif
  useEffect(() => {
    if (!todosData || todosData.categories.length <= 1) return;

    // Calculer le temps de lecture basé sur le nombre d'éléments dans la catégorie actuelle
    const currentCategory = todosData.categories[currentCategoryIndex];
    const itemCount = currentCategory?.todos?.length || 0;
    
    // Temps de base : 5 secondes minimum
    // + 2 secondes par élément pour la lecture
    const readingTime = Math.max(5000, 5000 + (itemCount * 2000));
    
    const rotationInterval = setInterval(() => {
      setCurrentCategoryIndex(prev => (prev + 1) % todosData.categories.length);
      setCurrentRowIndex(0); // Reset row index when changing category
      
      // Reset scroll position when changing category
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = 0;
      }
    }, readingTime);

    return () => clearInterval(rotationInterval);
  }, [todosData, currentCategoryIndex]);

  // Reset row index when category changes
  useEffect(() => {
    setCurrentRowIndex(0);
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = 0;
    }
  }, [currentCategoryIndex]);

  // Auto-scroll vertical doux (même système que Weekly Planning)
  useEffect(() => {
    if (!isAutoScrolling || !todosData?.categories) return;

    const currentTodos = getCurrentCategoryTodos();
    if (currentTodos.length === 0) return;

    const interval = setInterval(() => {
      setCurrentRowIndex(prev => {
        const nextIndex = (prev + 1) % currentTodos.length;
        
        // Scroll vers la ligne actuelle
        if (scrollContainerRef.current) {
          const container = scrollContainerRef.current;
          const rowHeight = 100; // hauteur approximative d'une ligne de todo (augmentée)
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
  }, [isAutoScrolling, todosData, currentCategoryIndex]);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://192.168.1.45:8000/api/v1/dashboard2/todos', {
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

      setTodosData(result.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion à l\'API');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircleSolid className="h-5 w-5 text-green-500" />;
      case 'in_progress':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'pending':
      default:
        return <CheckCircleIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'pending':
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return null;
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateStr; // Return original string if parsing fails
    }
  };

  const isUrgent = (dueDate: string | undefined) => {
    if (!dueDate) return false;
    try {
      const due = new Date(dueDate);
      const now = new Date();
      const diffTime = due.getTime() - now.getTime();
      const diffDays = diffTime / (1000 * 3600 * 24);
      return diffDays <= 7 && diffDays >= 0;
    } catch {
      return false;
    }
  };

  const getCurrentCategoryTodos = () => {
    if (!todosData || todosData.categories.length === 0) return [];

    const currentCategory = todosData.categories[currentCategoryIndex];
    if (!currentCategory) return [];

    const todos = currentCategory.todos;
    
    // Organiser : en cours et en attente en haut, terminées en bas
    const pendingTodos = todos.filter(todo => 
      todo.status.toLowerCase() === 'pending' || todo.status.toLowerCase() === 'in_progress'
    );
    const completedTodos = todos.filter(todo => 
      todo.status.toLowerCase() === 'completed'
    );

    // Trier les en cours/en attente par urgence
    const sortedPending = pendingTodos.sort((a, b) => {
      const aUrgent = isUrgent(a.due_date);
      const bUrgent = isUrgent(b.due_date);
      if (aUrgent && !bUrgent) return -1;
      if (!aUrgent && bUrgent) return 1;
      return 0;
    });

    return [...sortedPending, ...completedTodos];
  };

  const currentTodos = getCurrentCategoryTodos();

  const getCurrentCategory = () => {
    if (!todosData || todosData.categories.length === 0) return null;
    return todosData.categories[currentCategoryIndex];
  };

  if (loading) {
    return (
      <div className={`h-full flex flex-col ${className}`}>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Todos Google Sheets</h3>
          </div>
          <div className="flex-1 p-4">
            <div className="animate-pulse space-y-3 h-full">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`h-full flex flex-col ${className}`}>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Todos Google Sheets</h3>
          </div>
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
              <button 
                onClick={fetchTodos}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Réessayer
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!todosData || todosData.categories.length === 0) {
    return (
      <div className={`h-full flex flex-col ${className}`}>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Todos Google Sheets</h3>
          </div>
          <div className="flex-1 flex items-center justify-center p-4">
            <p className="text-center text-gray-500 dark:text-gray-400">Aucune donnée disponible</p>
          </div>
        </div>
      </div>
    );
  }

  const currentCategory = getCurrentCategory();

  return (
    <div className={`h-full flex flex-col ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col overflow-hidden">
        {/* Header avec titre de catégorie et navigation */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                {currentCategory?.category || 'Todos'}
              </h3>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
            
            {/* Indicateur de rotation */}
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
              <span>{currentCategoryIndex + 1}/{todosData.categories.length}</span>
              <div className="flex gap-1">
                {todosData.categories.map((_, idx) => (
                  <div
                    key={idx}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      idx === currentCategoryIndex ? 'bg-blue-500 scale-125' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
          
          {/* Stats de la catégorie courante */}
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="bg-white dark:bg-gray-700 rounded-lg py-3 px-3">
              <div className="text-lg font-bold text-gray-800 dark:text-white">{currentCategory?.total_count || 0}</div>
              <div className="text-sm text-gray-600 dark:text-gray-300">Total</div>
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-lg py-3 px-3">
              <div className="text-lg font-bold text-yellow-600">{currentCategory?.pending_count || 0}</div>
              <div className="text-sm text-gray-600 dark:text-gray-300">En cours</div>
            </div>
            <div className="bg-white dark:bg-gray-700 rounded-lg py-3 px-3">
              <div className="text-lg font-bold text-green-600">{currentCategory?.completed_count || 0}</div>
              <div className="text-sm text-gray-600 dark:text-gray-300">Terminés</div>
            </div>
          </div>
        </div>

        {/* Liste des todos avec auto-scroll doux */}
        <div 
          ref={scrollContainerRef}
          className="flex-1 overflow-y-auto p-3 space-y-2"
          style={{ scrollBehavior: 'smooth' }}
          onMouseEnter={() => setIsAutoScrolling(false)}
          onMouseLeave={() => setIsAutoScrolling(true)}
        >
          {currentTodos.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500 dark:text-gray-400 text-center">
                Aucun todo dans cette catégorie
              </p>
            </div>
          ) : (
            <>
              {currentTodos.map((todo, index) => {
                const isCompleted = todo.status.toLowerCase() === 'completed';
                const isFirstCompletedTask = isCompleted && 
                  (index === 0 || currentTodos[index - 1].status.toLowerCase() !== 'completed');
                const hasCompletedTasks = currentTodos.some(t => t.status.toLowerCase() === 'completed');
                const hasNonCompletedTasks = currentTodos.some(t => t.status.toLowerCase() !== 'completed');
                
                return (
                  <React.Fragment key={todo.id}>
                    {/* Séparateur avant les tâches terminées */}
                    {isFirstCompletedTask && hasNonCompletedTasks && hasCompletedTasks && (
                      <div className="flex items-center my-4">
                        <div className="flex-1 h-px bg-gray-300 dark:bg-gray-600"></div>
                        <span className="px-3 text-xs text-gray-500 dark:text-gray-400 font-medium bg-white dark:bg-gray-800">
                          Tâches terminées
                        </span>
                        <div className="flex-1 h-px bg-gray-300 dark:bg-gray-600"></div>
                      </div>
                    )}
                    
                    <div
                      className={`p-4 border rounded-lg transition-all duration-200 ${getStatusColor(todo.status)} ${
                        isUrgent(todo.due_date) ? 'ring-2 ring-red-300 dark:ring-red-600' : ''
                      } ${isCompleted ? 'opacity-75' : ''}`}
                    >
                      <div className="flex items-start gap-3">
                        {getStatusIcon(todo.status)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className={`text-base font-semibold truncate flex-1 ${
                              isCompleted ? 'line-through text-gray-500 dark:text-gray-400' : ''
                            }`}>
                              {todo.title}
                            </h4>
                            {isUrgent(todo.due_date) && !isCompleted && (
                              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0" />
                            )}
                          </div>
                          
                          <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
                            {todo.assigned_to && (
                              <div className="flex items-center gap-1">
                                <UserIcon className="h-4 w-4" />
                                <span className="truncate max-w-24 font-medium">{todo.assigned_to}</span>
                              </div>
                            )}
                            {todo.due_date && (
                              <div className="flex items-center gap-1">
                                <CalendarIcon className="h-4 w-4" />
                                <span className="font-medium">{formatDate(todo.due_date)}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </React.Fragment>
                );
              })}
            </>
          )}
        </div>

        {/* Footer avec indicateur de défilement */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
            <span className="font-medium">
              {currentTodos.length} todo{currentTodos.length !== 1 ? 's' : ''}
            </span>
            <div className="flex items-center gap-2">
              {isAutoScrolling && <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>}
              <span className="font-medium">Auto-scroll {isAutoScrolling ? 'ON' : 'OFF'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TodosList;