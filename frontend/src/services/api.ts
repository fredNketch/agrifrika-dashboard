/**
 * Service API pour Dashboard AGRIFRIKA
 * Connexion aux endpoints backend pour récupérer les vraies données
 */

import type { 
  TeamAvailabilityData,
  WeeklyPlanningData, 
  CashFlowData,
  ActionPlanItem,
  BasecampData,
  FacebookVideoData,
  Dashboard2Response,
  TodosData
} from '../types';

const API_BASE_URL = 'http://192.168.1.45:8000/api/v1';

interface APIResponse<T> {
  success: boolean;
  data: T;
  message: string;
  last_updated?: string;
}

class DashboardAPI {
  private async fetchAPI<T>(endpoint: string): Promise<T> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200000); // 60s timeout (1 minute)
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        // Pour éviter les problèmes CORS en développement
        mode: 'cors',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: APIResponse<T> = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'API call failed');
      }

      return result.data;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error(`Timeout: ${endpoint} prend trop de temps`);
      }
      throw new Error(`Impossible de récupérer les données: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
    }
  }

  /**
   * Récupère toutes les données du Dashboard 2 en une seule requête
   */
  async getDashboard2Complete(): Promise<Dashboard2Response> {
    return this.fetchAPI<Dashboard2Response>('/dashboard2/complete');
  }

  /**
   * Récupère les données de disponibilité de l'équipe
   */
  async getTeamAvailability(): Promise<TeamAvailabilityData> {
    return this.fetchAPI<TeamAvailabilityData>('/dashboard2/team-availability');
  }

  /**
   * Récupère le planning hebdomadaire
   */
  async getWeeklyPlanning(): Promise<WeeklyPlanningData> {
    return this.fetchAPI<WeeklyPlanningData>('/dashboard2/weekly-planning');
  }

  /**
   * Récupère les données de cash flow
   */
  async getCashFlow(): Promise<CashFlowData> {
    return this.fetchAPI<CashFlowData>('/dashboard2/cash-flow');
  }

  /**
   * Récupère les items du plan d'action
   */
  async getActionPlan(): Promise<ActionPlanItem[]> {
    return this.fetchAPI<ActionPlanItem[]>('/dashboard2/action-plan');
  }

  /**
   * Récupère les todos Basecamp
   */
  async getBasecampTodos(): Promise<BasecampData> {
    return this.fetchAPI<BasecampData>('/dashboard2/basecamp-todos');
  }

  /**
   * Récupère la vidéo Facebook
   */
  async getFacebookVideo(): Promise<FacebookVideoData | null> {
    try {
      return await this.fetchAPI<FacebookVideoData>('/dashboard2/facebook-video');
    } catch (error) {
      // La vidéo Facebook peut ne pas être disponible
      console.warn('Aucune vidéo Facebook disponible');
      return null;
    }
  }

  /**
   * Récupère tous les todos depuis Google Sheets
   */
  async getTodos(): Promise<TodosData> {
    return this.fetchAPI<TodosData>('/dashboard2/todos');
  }

  /**
   * Récupère toutes les données KPI pour Dashboard 1
   */
  async getDashboard1KPIs(): Promise<any> {
    return this.fetchAPI<any>('/dashboard1/kpis');
  }

  /**
   * Récupère les données d'engagement public pour Dashboard 1 (déprécié - utiliser getDashboard1KPIs)
   */
  async getPublicEngagement(): Promise<any> {
    return this.fetchAPI<any>('/dashboard1/engagement');
  }

  /**
   * Récupère les données de fundraising pipeline pour Dashboard 1 (déprécié - utiliser getDashboard1KPIs)
   */
  async getFundraisingPipeline(): Promise<any> {
    return this.fetchAPI<any>('/dashboard1/fundraising');
  }

  /**
   * Récupère les vraies tendances de fundraising basées sur les cumuls
   */
  async getFundraisingTrends(): Promise<any[]> {
    return this.fetchAPI<any[]>('/dashboard1/fundraising/trends');
  }

  /**
   * Récupère les tendances mensuelles d'engagement public
   */
  async getPublicEngagementTrends(): Promise<any[]> {
    return this.fetchAPI<any[]>('/dashboard1/public-engagement/trends');
  }

  /**
   * Force le rafraîchissement du cache des données
   */
  async refreshCache(): Promise<void> {
    await this.fetchAPI<void>('/refresh-cache');
  }
}

// Instance singleton
export const dashboardAPI = new DashboardAPI();

/**
 * Hook personnalisé pour utiliser l'API
 */
export const useDashboardAPI = () => {
  return {
    api: dashboardAPI
  };
};

export default dashboardAPI;