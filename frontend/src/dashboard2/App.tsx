import { useState, useEffect } from 'react';
import { 
  TeamAvailability, 
  WeeklyPlanning, 
  CashFlowMonitor, 
  ActionPlan, 
  BasecampTodos,
  FacebookVideo,
  TodosList
} from '../components/dashboard2';
import { Dashboard2FullscreenLayout } from '../components/shared';
import Header from '../components/ui/Header';


function Dashboard2App() {
  // Chaque composant gère maintenant son propre chargement de données

  // Plus de configuration de blocs rotatifs - Layout opérationnel fixe

  return (
    <div className="h-screen dashboard2-layout flex flex-col overflow-hidden text-reduced">
      {/* Header avec titre Dashboard 2 */}
      <Header 
        title="Dashboard Opérationnel - Écran 2" 
        showControls={true}
        className="flex-shrink-0"
      />

      {/* Contenu principal - Dashboard 2 Fullscreen - Rotation plein écran 3 minutes par bloc */}
      <main className="flex-1 overflow-hidden">
        <Dashboard2FullscreenLayout
          teamAvailability={<TeamAvailability />}
          weeklyPlanning={<WeeklyPlanning />}
          basecampTodos={<TodosList />}
          facebookVideo={<FacebookVideo />}
          cashFlow={<CashFlowMonitor />}
        />
      </main>

      {/* Footer - Compatible dark mode */}
      <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-4 py-1 flex-shrink-0">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div>Dashboard Opérationnel - Écran 2</div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-1.5 h-1.5 bg-agrifrika-green rounded-full animate-pulse"></div>
              <span>Temps réel</span>
            </div>
            <div>v1.0.0</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard2App;