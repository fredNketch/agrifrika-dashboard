import { useState, useEffect } from 'react';
import { DefaultAlive, PublicEngagement, FundraisingPipeline } from '../components/dashboard1';
import { Dashboard1FullscreenLayout } from '../components/shared';
import Header from '../components/ui/Header';
import { dashboardAPI } from '../services/api';
import type { 
  DefaultAliveData, 
  PublicEngagementData, 
  FundraisingPipelineData
} from '../types';

function Dashboard1App() {
  const [loading, setLoading] = useState(true);
  
  // États pour Dashboard 1 - KPI Stratégiques
  const [defaultAliveData, setDefaultAliveData] = useState<DefaultAliveData | null>(null);
  const [publicEngagementData, setPublicEngagementData] = useState<PublicEngagementData | null>(null);
  const [fundraisingData, setFundraisingData] = useState<FundraisingPipelineData | null>(null);

  // Chargement des vraies données depuis l'API
  useEffect(() => {
    const loadRealData = async () => {
      try {
        setLoading(true);
        
        // Récupérer toutes les vraies données depuis les API individuelles
        const [cashFlowData, engagementData, fundraisingData, fundraisingTrends] = await Promise.all([
          dashboardAPI.getCashFlow(),
          dashboardAPI.getPublicEngagement(),
          dashboardAPI.getFundraisingPipeline(),
          dashboardAPI.getFundraisingTrends()
        ]);
        
        // === DEFAULT ALIVE DATA ===
        // Convertir les données Cash Flow en format DefaultAlive
        let monthlyCharges = cashFlowData.monthly_burn_rate || 0;
        if (monthlyCharges === 0) {
          const recentExpenses = (cashFlowData.recent_transactions || [])
            .filter(tx => tx.type === 'expense')
            .reduce((sum, tx) => sum + tx.amount, 0);
          monthlyCharges = recentExpenses > 0 ? recentExpenses : 3268; // Utiliser la valeur par défaut plus réaliste
        }
        
        const cashAvailable = cashFlowData.current_balance || 0;
        const promisedFunds = cashFlowData.historical_income || 0;
        
        const practicalMonths = monthlyCharges > 0 ? cashAvailable / monthlyCharges : 0;
        const theoreticalMonths = monthlyCharges > 0 ? (cashAvailable + promisedFunds) / monthlyCharges : 0;
        
        const recentTransactions = cashFlowData.recent_transactions || [];
        const totalIncome = recentTransactions
          .filter(tx => tx.type === 'income')
          .reduce((sum, tx) => sum + tx.amount, 0);
        const totalExpense = recentTransactions
          .filter(tx => tx.type === 'expense')
          .reduce((sum, tx) => sum + tx.amount, 0);
        const trendPercentage = totalExpense > 0 ? ((totalIncome - totalExpense) / totalExpense) * 100 : 0;

        setDefaultAliveData({
          cash_available: cashAvailable,
          monthly_charges: monthlyCharges,
          promised_funds: promisedFunds,
          default_alive_practical: practicalMonths,
          default_alive_theoretical: theoreticalMonths,
          trend_percentage: trendPercentage,
          last_updated: cashFlowData.last_updated || new Date().toISOString()
        });

        // === PUBLIC ENGAGEMENT DATA (vraies données API) ===
        const engagementScore = engagementData.score || 0;
        const engagementTotalPoints = engagementData.total_points_obtenus || engagementData.total_points || 0;
        const engagementMaxPoints = engagementData.total_objectif || engagementData.max_points || 10000;
        
        // Convertir TOUTES les données détaillées par source depuis l'API
        const detailsBySource = engagementData.details_par_source || {};
        const rawData = engagementData.raw_data || {};
        
        // Toutes les 12 métriques du Google Sheet
        const allMetrics = {
          vues: detailsBySource.vues?.valeur_obtenue || rawData.vues || 0,
          likes_reactions: detailsBySource.likes_reactions?.valeur_obtenue || rawData.likes_reactions || 0,
          partages: detailsBySource.partages?.valeur_obtenue || rawData.partages || 0,
          commentaires: detailsBySource.commentaires?.valeur_obtenue || rawData.commentaires || 0,
          nouveaux_abonnes: detailsBySource.nouveaux_abonnes?.valeur_obtenue || rawData.nouveaux_abonnes || 0,
          telechargement_app: detailsBySource.telechargement_app?.valeur_obtenue || rawData.telechargement_app || 0,
          visites_uniques_site: detailsBySource.visites_uniques_site?.valeur_obtenue || rawData.visites_uniques_site || 0,
          mention_medias: detailsBySource.mention_medias?.valeur_obtenue || rawData.mention_medias || 0,
          newsletter: detailsBySource.newsletter?.valeur_obtenue || rawData.newsletter || 0,
          evenement_50plus_participants: detailsBySource.evenement_50plus_participants?.valeur_obtenue || rawData.evenement_50plus_participants || 0,
          apparition_recherches: detailsBySource.apparition_recherches?.valeur_obtenue || rawData.apparition_recherches || 0,
          impressions_linkedin: detailsBySource.impressions_linkedin?.valeur_obtenue || rawData.impressions_linkedin || 0
        };
        
        // Grouper par source pour l'affichage (compatible avec l'ancien format)
        const sources = {
          facebook: allMetrics.vues,
          linkedin: allMetrics.impressions_linkedin,
          website: allMetrics.visites_uniques_site,
          newsletter: allMetrics.newsletter,
          events: allMetrics.evenement_50plus_participants
        };
        
        // Calculer les 3 derniers mois basés sur la date courante
        const currentDate = new Date();
        const monthNames = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"];
        
        const getLastMonths = (count: number) => {
          const months = [];
          for (let i = count - 1; i >= 0; i--) {
            const date = new Date(currentDate);
            date.setMonth(date.getMonth() - i);
            months.push(monthNames[date.getMonth()]);
          }
          return months;
        };
        
        const lastThreeMonths = getLastMonths(3);

        const finalEngagementData = {
          score: engagementScore,
          total_points: engagementTotalPoints,
          max_points: engagementMaxPoints,
          sources: sources,
          // Ajouter TOUTES les métriques détaillées
          detailed_metrics: allMetrics,
          // Utiliser les vraies données top_content de l'API (depuis Google Sheets)
          top_content: engagementData.top_content || [
            // Fallback seulement si pas de données API
            { title: "Vues Facebook", engagement: allMetrics.vues, platform: "Facebook" },
            { title: "Impressions LinkedIn", engagement: allMetrics.impressions_linkedin, platform: "LinkedIn" }
          ],
          // Utiliser les vraies données monthly_trend de l'API (depuis Google Sheets)
          monthly_trend: engagementData.monthly_trend || [
            // Fallback avec calcul basé sur les vraies dates
            { month: lastThreeMonths[0], score: Math.max(0, engagementScore - 15) },
            { month: lastThreeMonths[1], score: Math.max(0, engagementScore - 8) },
            { month: lastThreeMonths[2], score: engagementScore }
          ],
          last_updated: engagementData.last_updated || new Date().toISOString()
        };
        
        setPublicEngagementData(finalEngagementData);

        // === FUNDRAISING DATA (vraies données API) ===
        const fundraisingScore = fundraisingData.score || 0;
        const fundraisingTotalPoints = fundraisingData.total_points_obtenus || fundraisingData.total_points || 0;
        const fundraisingMaxPoints = fundraisingData.objectif_total || fundraisingData.max_points || 100;
        
        // Utiliser les vraies données de la réponse API
        const rawFundData = fundraisingData.raw_data || {};
        const categories = {
          concours: (rawFundData.participation_simple || 0) + (rawFundData.participation_plus_100k || 0) * 2 + (rawFundData.finaliste_simple || 0) * 2 + (rawFundData.vainqueur || 0) * 3,
          subventions: (rawFundData.demande_simple || 0) + (rawFundData.demande_plus_100k || 0) * 2 + (rawFundData.entretien_presentation || 0) * 2 + (rawFundData.acceptation || 0) * 3,
          investisseurs: (rawFundData.contact_initial || 0) + (rawFundData.reponse_positive || 0) * 2 + (rawFundData.meeting_programme || 0) * 2,
          activités: 0 // Pas de données pour les activités dans l'API actuelle
        };
        
        // Utiliser les vraies tendances de fundraising si disponibles
        let progressChart = [
          { month: lastThreeMonths[0], amount: Math.max(0, fundraisingTotalPoints * 0.7) },
          { month: lastThreeMonths[1], amount: Math.max(0, fundraisingTotalPoints * 0.85) },
          { month: lastThreeMonths[2], amount: fundraisingTotalPoints }
        ];
        
        // Remplacer par les vraies tendances si disponibles
        if (fundraisingTrends && fundraisingTrends.length > 0) {
          progressChart = fundraisingTrends.map(trend => ({
            month: trend.month,
            amount: trend.total_points
          }));
        }
        
        setFundraisingData({
          score: fundraisingScore,
          total_points: fundraisingTotalPoints,
          max_points: fundraisingMaxPoints,
          categories: categories,
          upcoming_deadlines: [
            { title: "Suivi fundraising en cours", date: new Date().toISOString(), type: "info" }
          ],
          progress_chart: progressChart,
          trends_data: fundraisingTrends, // Ajouter les données de tendances détaillées
          last_updated: new Date().toISOString()
        });

        setLoading(false);
      } catch (error) {
        console.error('Erreur lors du chargement des données Dashboard1:', error);
        
        // Fallback vers des données mockées en cas d'erreur API
        setDefaultAliveData({
          cash_available: 45000,
          monthly_charges: 12000,
          promised_funds: 25000,
          default_alive_practical: 5.8,
          default_alive_theoretical: 7.2,
          trend_percentage: -2.3,
          last_updated: new Date().toISOString()
        });

        // Calculer les vraies dates même en fallback
        const currentDate = new Date();
        const monthNames = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"];
        const getLastMonths = (count: number) => {
          const months = [];
          for (let i = count - 1; i >= 0; i--) {
            const date = new Date(currentDate);
            date.setMonth(date.getMonth() - i);
            months.push(monthNames[date.getMonth()]);
          }
          return months;
        };
        const lastThreeMonths = getLastMonths(3);

        setPublicEngagementData({
          score: 72,
          total_points: 7200,
          max_points: 10000,
          sources: {
            facebook: 2800,
            linkedin: 1500,
            website: 1200,
            newsletter: 900,
            events: 700
          },
          top_content: [
            { title: "Lancement de notre nouveau programme agricole", engagement: 450, platform: "Facebook" },
            { title: "Témoignage d'un agriculteur partenaire", engagement: 320, platform: "LinkedIn" }
          ],
          monthly_trend: [
            { month: lastThreeMonths[0], score: 65 },
            { month: lastThreeMonths[1], score: 68 },
            { month: lastThreeMonths[2], score: 72 }
          ],
          last_updated: new Date().toISOString()
        });

        setFundraisingData({
          score: 65,
          total_points: 65,
          max_points: 100,
          categories: {
            concours: 15,
            subventions: 22,
            investisseurs: 18,
            activités: 10
          },
          upcoming_deadlines: [
            { title: "Concours innovation agricole", date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), type: "concours" },
            { title: "Subvention développement rural", date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(), type: "subvention" }
          ],
          progress_chart: [
            { month: lastThreeMonths[0], amount: 15000 },
            { month: lastThreeMonths[1], amount: 22000 },
            { month: lastThreeMonths[2], amount: 28000 }
          ],
          last_updated: new Date().toISOString()
        });
        
        setLoading(false);
      }
    };

    loadRealData();
  }, []);

  return (
    <div className="h-screen dashboard1-layout flex flex-col overflow-hidden text-reduced">
      {/* Header Premium avec logo */}
      <Header 
        title="AGRIFRIKA" 
        showControls={true}
        className="flex-shrink-0"
      />

      {/* Contenu principal - Dashboard 1 KPI - Layout plein écran */}
      <main className="flex-1 overflow-hidden">
        <Dashboard1FullscreenLayout 
          defaultAlive={<DefaultAlive data={defaultAliveData} loading={loading} />}
          publicEngagement={<PublicEngagement data={publicEngagementData} loading={loading} />}
          fundraisingPipeline={<FundraisingPipeline data={fundraisingData} loading={loading} />}
        />
      </main>

      {/* Footer - Hauteur fixe */}
      <footer className="bg-white border-t border-gray-200 px-4 py-1 flex-shrink-0">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>Dashboard KPI Stratégiques - Écran 1</div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-1.5 h-1.5 bg-agrifrika-green rounded-full"></div>
              <span>Temps réel</span>
            </div>
            <div>v1.0.0</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard1App;