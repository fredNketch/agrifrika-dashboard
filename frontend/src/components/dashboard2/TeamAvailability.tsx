import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import AnimatedCard from '../ui/AnimatedCard';
import type { TeamAvailabilityData, DetailedTeamMember, AvailabilityStatus } from '../../types';

interface TeamAvailabilityProps {
  className?: string;
}

const TeamAvailability: React.FC<TeamAvailabilityProps> = ({ className = '' }) => {
  const [data, setData] = useState<TeamAvailabilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentRowIndex, setCurrentRowIndex] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const staffScrollRef = React.useRef<HTMLDivElement>(null);
  const gridScrollRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchTeamAvailability();
    const interval = setInterval(fetchTeamAvailability, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);



  const fetchTeamAvailability = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://dashboard.agrifrika.com/api/v1/dashboard2/team-availability', {
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

  // Calculer la semaine ISO courante (exactement comme Python's isocalendar())
  const getCurrentWeekNumber = (): number => {
    const currentDate = new Date();
    
    // Créer une date temporaire pour le calcul ISO
    const tempDate = new Date(currentDate.getTime());
    tempDate.setHours(0, 0, 0, 0);
    
    // Ajuster pour le jeudi (ISO week definition)
    tempDate.setDate(tempDate.getDate() + 3 - (tempDate.getDay() + 6) % 7);
    
    // Calculer le 1er janvier de la même année
    const year = tempDate.getFullYear();
    const jan1 = new Date(year, 0, 1);
    
    // Calculer la différence en semaines
    const weekNumber = Math.ceil((((tempDate.getTime() - jan1.getTime()) / 86400000) + 1) / 7);
    
    return weekNumber;
  };

  const currentWeek = getCurrentWeekNumber();

  // Utiliser les données détaillées réelles de l'API
  const detailedMembers: DetailedTeamMember[] = (data?.detailed_members && Array.isArray(data.detailed_members) && data.detailed_members.length > 0) 
    ? data.detailed_members 
    : [];

  // Auto-scroll vertical doux (même système que Weekly Planning et TodosList)
  useEffect(() => {
    if (!isAutoScrolling || !detailedMembers || detailedMembers.length === 0) return;

    const interval = setInterval(() => {
      setCurrentRowIndex(prev => {
        const nextIndex = (prev + 1) % detailedMembers.length;
        
        // Scroll vers la ligne actuelle (synchroniser les deux conteneurs)
        const staffContainer = staffScrollRef.current;
        const gridContainer = gridScrollRef.current;
        
        if (staffContainer && gridContainer) {
          const rowHeight = 48; // hauteur d'une ligne (h-12)
          const scrollTop = nextIndex * rowHeight;
          
          staffContainer.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
          
          gridContainer.scrollTo({
            top: scrollTop,
            behavior: 'smooth'
          });
        }
        
        return nextIndex;
      });
    }, 2000); // Change toutes les 2 secondes

    return () => clearInterval(interval);
  }, [isAutoScrolling, detailedMembers]);

  // Reset du scroll quand les données changent
  useEffect(() => {
    setCurrentRowIndex(0);
    if (staffScrollRef.current) {
      staffScrollRef.current.scrollTop = 0;
    }
    if (gridScrollRef.current) {
      gridScrollRef.current.scrollTop = 0;
    }
  }, [detailedMembers]);

  // Format Google Sheets complet : 7 jours avec Matin/Soir
  const weekDays = [
    { day: 'lundi', short: 'Lun' },
    { day: 'mardi', short: 'Mar' },
    { day: 'mercredi', short: 'Mer' },
    { day: 'jeudi', short: 'Jeu' },
    { day: 'vendredi', short: 'Ven' },
    { day: 'samedi', short: 'Sam' },
    { day: 'dimanche', short: 'Dim' }
  ];

  // Pas de scroll automatique - affichage complet

  // Fonction pour récupérer le statut réel depuis les données détaillées
  const getRealStatus = (member: DetailedTeamMember, dayName: string, period: 'morning' | 'evening'): AvailabilityStatus | null => {
    const daySchedule = member.weekly_schedule.find(day => day.day.toLowerCase() === dayName.toLowerCase());
    if (!daySchedule) return null;
    
    return period === 'morning' ? daySchedule.morning || null : daySchedule.evening || null;
  };

  // Calcul du pourcentage de disponibilité avec logique métier correcte
  const calculateRealAvailabilityRate = (): number => {
    if (!detailedMembers || detailedMembers.length === 0) return 0;

    let totalWorkSlots = 0;   // Créneaux de travail obligatoires (semaine + remplis weekend)
    let availableSlots = 0;   // Créneaux disponibles (office/online)

    // Jours de semaine où la présence est obligatoire
    const workDays = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi'];

    detailedMembers.forEach(member => {
      member.weekly_schedule.forEach(daySchedule => {
        const isWorkDay = workDays.includes(daySchedule.day.toLowerCase());
        
        // Matin
        if (isWorkDay) {
          // En semaine : toujours compter (null, vide ou unavailable = absent)
          totalWorkSlots++;
          if (daySchedule.morning === 'office' || daySchedule.morning === 'online') {
            availableSlots++;
          }
          // Si null, vide ou unavailable : 0 point (absence)
        } else {
          // Weekend : compter seulement si rempli (pas null et pas vide)
          if (daySchedule.morning && typeof daySchedule.morning === 'string' && daySchedule.morning.trim() !== '') {
            totalWorkSlots++;
            if (daySchedule.morning === 'office' || daySchedule.morning === 'online') {
              availableSlots++;
            }
          }
        }
        
        // Soir (même logique)
        if (isWorkDay) {
          // En semaine : toujours compter (null, vide ou unavailable = absent)
          totalWorkSlots++;
          if (daySchedule.evening === 'office' || daySchedule.evening === 'online') {
            availableSlots++;
          }
          // Si null, vide ou unavailable : 0 point (absence)
        } else {
          // Weekend : compter seulement si rempli (pas null et pas vide)
          if (daySchedule.evening && typeof daySchedule.evening === 'string' && daySchedule.evening.trim() !== '') {
            totalWorkSlots++;
            if (daySchedule.evening === 'office' || daySchedule.evening === 'online') {
              availableSlots++;
            }
          }
        }
      });
    });

    return totalWorkSlots > 0 ? (availableSlots / totalWorkSlots) * 100 : 0;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'office': 
        return { 
          bg: 'bg-green-600', 
          text: 'text-white', 
          label: 'Office'
        };
      case 'online': 
        return { 
          bg: 'bg-blue-600', 
          text: 'text-white', 
          label: 'Online'
        };
      case 'unavailable': 
        return { 
          bg: 'bg-red-600', 
          text: 'text-white', 
          label: 'Unavailable'
        };
      default: 
        return { 
          bg: '', 
          text: '', 
          label: '',
          style: 'w-full h-6'
        };
    }
  };

  return (
    <div className={`h-full w-full flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden ${className}`}>
      {/* Header ultra-compact */}
      <div className="px-3 py-1 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-emerald-700 to-emerald-800 text-white flex-shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-lg">👥</span>
          <h3 className="text-sm font-semibold">Team Availability</h3>
          <span className="text-xs opacity-90">W{currentWeek}</span>
        </div>
      </div>

      {/* Container principal - utilisation complète de l'espace */}
      <div 
        className="flex-1 flex overflow-hidden"
        onMouseEnter={() => setIsAutoScrolling(false)}
        onMouseLeave={() => setIsAutoScrolling(true)}
      >
        {/* Colonne Staff - largeur augmentée */}
        <div className="w-40 flex-shrink-0 flex flex-col border-r border-gray-200 dark:border-gray-700">
          {/* Header Staff */}
          <div className="h-12 bg-emerald-700 text-white flex items-center justify-center border-b border-emerald-800">
            <span className="text-sm font-bold">Staff</span>
          </div>
          
          {/* Liste des noms - avec auto-scroll */}
          <div ref={staffScrollRef} className="flex-1 bg-gray-50 dark:bg-gray-800 overflow-y-auto">
            {detailedMembers.length > 0 ? detailedMembers.map((member, memberIndex) => (
              <motion.div
                key={`staff-${memberIndex}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: memberIndex * 0.02 }}
                className="h-12 px-3 flex items-center border-b border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center gap-2 w-full">
                  <span className={`w-3 h-3 rounded-full flex-shrink-0 shadow-sm ${
                    member.overall_status === 'office' ? 'bg-green-500' :
                    member.overall_status === 'online' ? 'bg-blue-500' : 'bg-red-500'
                  }`}></span>
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-100 leading-tight" title={member.name}>
                    {member.name}
                  </span>
                </div>
              </motion.div>
            )) : (
              <div className="p-4 text-center">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {loading ? 'Chargement...' : 'Aucune donnée disponible'}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Grille des disponibilités - utilisation complète de l'espace restant */}
        <div className="flex-1 flex flex-col">
            {/* Header des jours */}
          <div className="h-12 flex bg-gray-700 dark:bg-gray-900 text-white border-b border-gray-600">
              {weekDays.map((day, dayIndex) => (
              <div key={`header-${dayIndex}`} className="flex-1 flex flex-col border-r border-gray-600 last:border-r-0">
                <div className="flex-1 flex items-center justify-center text-sm font-bold bg-gray-600">
                    {day.short}
                  </div>
                <div className="h-5 flex bg-gray-700 border-t border-gray-600">
                    <div className="flex-1 text-xs text-center border-r border-gray-600 flex items-center justify-center font-medium">M</div>
                    <div className="flex-1 text-xs text-center flex items-center justify-center font-medium">S</div>
                  </div>
                </div>
              ))}
            </div>

          {/* Grille des statuts - avec auto-scroll synchronisé */}
          <div ref={gridScrollRef} className="flex-1 overflow-y-auto">
              {detailedMembers.length > 0 ? detailedMembers.map((member, memberIndex) => (
                <motion.div
                  key={`grid-${memberIndex}`}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: memberIndex * 0.02 }}
                className="h-12 flex border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                >
                  {weekDays.map((day, dayIndex) => {
                    const morningStatus = getRealStatus(member, day.day, 'morning');
                    const eveningStatus = getRealStatus(member, day.day, 'evening');
                    
                    return (
                    <div key={`cell-${dayIndex}`} className="flex-1 flex border-r border-gray-200 dark:border-gray-700 last:border-r-0">
                        {/* Matin */}
                        <div className="flex-1 p-1 border-r border-gray-200 dark:border-gray-700 flex items-center justify-center">
                          {morningStatus ? (
                            <div className={`w-full h-full rounded-2xl flex items-center justify-center text-[10px] font-bold mx-1 my-0.5 ${
                              morningStatus === 'office' ? 'bg-green-500 text-white shadow-sm' :
                              morningStatus === 'online' ? 'bg-blue-500 text-white shadow-sm' :
                              morningStatus === 'unavailable' ? 'bg-red-500 text-white shadow-sm' :
                              'bg-gray-200 dark:bg-gray-600'
                            }`}>
                              {morningStatus === 'office' ? 'BUREAU' : 
                               morningStatus === 'online' ? 'EN LIGNE' : 
                               morningStatus === 'unavailable' ? 'ABSENT' : ''}
                            </div>
                          ) : (
                            <div className="w-full h-full bg-gray-100 dark:bg-gray-700 rounded-2xl mx-1 my-0.5"></div>
                          )}
                        </div>
                        
                        {/* Soir */}
                        <div className="flex-1 p-1 flex items-center justify-center">
                          {eveningStatus ? (
                            <div className={`w-full h-full rounded-2xl flex items-center justify-center text-[10px] font-bold mx-1 my-0.5 ${
                              eveningStatus === 'office' ? 'bg-green-500 text-white shadow-sm' :
                              eveningStatus === 'online' ? 'bg-blue-500 text-white shadow-sm' :
                              eveningStatus === 'unavailable' ? 'bg-red-500 text-white shadow-sm' :
                              'bg-gray-200 dark:bg-gray-600'
                            }`}>
                              {eveningStatus === 'office' ? 'BUREAU' : 
                               eveningStatus === 'online' ? 'EN LIGNE' : 
                               eveningStatus === 'unavailable' ? 'ABSENT' : ''}
                            </div>
                          ) : (
                            <div className="w-full h-full bg-gray-100 dark:bg-gray-700 rounded-2xl mx-1 my-0.5"></div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </motion.div>
              )) : null}
          </div>
        </div>
      </div>

      {/* Footer compact - hauteur réduite pour éviter le scroll vertical */}
      <div className="flex-shrink-0 bg-gradient-to-r from-emerald-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="px-3 py-2">
          <div className="flex items-center justify-between">
            {/* Pourcentage principal - plus compact */}
            <div className="flex-1 text-center">
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                {calculateRealAvailabilityRate().toFixed(1)}%
              </div>
              <div className="text-xs text-emerald-700 dark:text-emerald-300">
                Disponibilité • {detailedMembers.length} membres
              </div>
            </div>
            
            {/* Légende ultra-compacte à droite */}
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full shadow-sm"></div>
                <span className="text-gray-700 dark:text-gray-300">BUREAU</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full shadow-sm"></div>
                <span className="text-gray-700 dark:text-gray-300">EN LIGNE</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-red-500 rounded-full shadow-sm"></div>
                <span className="text-gray-700 dark:text-gray-300">ABSENT</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamAvailability;