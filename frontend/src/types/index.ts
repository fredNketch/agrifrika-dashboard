// Types pour le Dashboard AGRIFRIKA

// États généraux
export type Status = 'available' | 'occupied' | 'unavailable' | 'field';
export type Priority = 'P1' | 'P2' | 'P3' | 'P4';
export type TaskStatus = 'a_faire' | 'en_cours' | 'termine' | 'terminé' | 'non_validé' | 'validé';
export type TaskPriority = 'haute' | 'moyenne' | 'basse';

// Dashboard 1 - KPI Types
export interface DefaultAliveData {
  cash_available: number;
  monthly_charges: number;
  promised_funds: number;
  default_alive_practical: number;
  default_alive_theoretical: number;
  trend_percentage: number;
  last_updated: string;
}

export interface PublicEngagementData {
  score: number;
  total_points: number;
  max_points: number;
  sources: {
    facebook: number;
    linkedin: number;
    website: number;
    newsletter: number;
    events: number;
  };
  // Ajouter toutes les métriques détaillées
  detailed_metrics?: {
    vues: number;
    likes_reactions: number;
    partages: number;
    commentaires: number;
    nouveaux_abonnes: number;
    telechargement_app: number;
    visites_uniques_site: number;
    mention_medias: number;
    newsletter: number;
    evenement_50plus_participants: number;
    apparition_recherches: number;
    impressions_linkedin: number;
  };
  top_content: Array<{
    title: string;
    engagement: number;
    platform: string;
    url?: string;
    vues?: number;
  }>;
  monthly_trend: Array<{
    month: string;
    score: number; // pour compatibilité, peut contenir un pourcentage
    total_score?: number; // points mensuels totaux calculés côté backend
    entries_count?: number;
    total_vues?: number;
    total_likes?: number;
    total_partages?: number;
    total_commentaires?: number;
    total_abonnes?: number;
    month_key?: string;
  }>;
  last_updated: string;
}

export interface FundraisingPipelineData {
  score: number;
  total_points: number;
  max_points: number;
  categories: {
    concours: number;
    subventions: number;
    investisseurs: number;
    activités: number;
  };
  upcoming_deadlines: Array<{
    title: string;
    date: string;
    type: 'concours' | 'subvention' | 'investisseur';
  }>;
  progress_chart: Array<{
    month: string;
    amount: number;
  }>;
  trends_data?: Array<{
    month: string;
    base_points: number;
    activity_points: number;
    total_points: number;
    score: number;
    date: string;
    week: string;
  }>;
  last_updated: string;
}

// Dashboard 2 - Opérationnel Types
export interface TeamMember {
  id: string;
  name: string;
  position: string;
  priority: Priority;
  status: Status;
  workload: number;
  availability_notes?: string;
  last_seen?: string;
}

export interface WeeklyTask {
  id: string;
  title: string;
  assigned_to: string;
  priority: TaskPriority;
  status: TaskStatus;
  start_date: string;
  end_date: string;
  time: string;
  progress: number;
  description?: string;
}

export interface WeeklyPlanningData {
  week_number: number;
  year: number;
  week_start: string;
  week_end: string;
  daily_schedule: {
    [key: string]: {
      tasks: Array<{
        title: string;
        description: string;
        time: string;
        priority: 'high' | 'medium' | 'low';
      }>;
    };
  };
  today_priorities: Array<{
    title: string;
    assigned_to: string;
    time: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  weekly_meetings: Array<{
    title: string;
    participants: string[];
    datetime: string;
  }>;
  weekly_milestone?: {
    title: string;
    deadline: string;
  };
  completion_stats: {
    completed: number;
    total: number;
  };
  last_updated: string;
}

// Types pour les disponibilités détaillées
export type AvailabilityStatus = 'office' | 'online' | 'unavailable';

export interface DayAvailability {
  day: string;
  morning?: AvailabilityStatus;
  evening?: AvailabilityStatus;
}

export interface DetailedTeamMember {
  name: string;
  role?: string;
  weekly_schedule: DayAvailability[];
  overall_status: AvailabilityStatus;
  current_task?: string;
}

export interface TeamAvailabilityData {
  summary: {
    available: number;
    occupied: number;
    unavailable: number;
  };
  team_members: Array<{
    name: string;
    role?: string;
    status: 'office' | 'online' | 'unavailable' | 'available' | 'occupied';
    current_task?: string;
  }>;
  detailed_members: DetailedTeamMember[];
  upcoming_changes: Array<{
    member_name: string;
    change_type: string;
    description: string;
    scheduled_time: string;
  }>;
  weekly_availability_rate: number;
  last_updated: string;
}

export interface ProjectStatusData {
  summary: {
    completed: number;
    in_progress: number;
    on_hold: number;
    at_risk: number;
  };
  active_projects: Array<{
    name: string;
    status: 'completed' | 'in_progress' | 'on_hold' | 'at_risk';
    priority: 'high' | 'medium' | 'low';
    progress_percentage: number;
    project_manager: string;
    deadline: string;
  }>;
  upcoming_milestones: Array<{
    title: string;
    project_name: string;
    deadline: string;
  }>;
  resource_allocation: {
    teams: {
      [key: string]: number;
    };
    budget_used: number;
    total_budget: number;
  };
  alerts: Array<{
    message: string;
    severity: 'high' | 'medium' | 'low';
    project_name: string;
    created_at: string;
  }>;
  overall_performance: {
    on_time_percentage: number;
    budget_efficiency: number;
  };
  last_updated: string;
}

export interface CashFlowData {
  current_balance: number;
  balance_date: string;
  weekly_summary: {
    total_income: number;
    total_expenses: number;
    net_change: number;
  };
  daily_evolution: Array<{
    date: string;
    amount: number;
  }>;
  recent_transactions: Array<{
    type: 'income' | 'expense' | 'transfer';
    description: string;
    amount: number;
    date: string;
    category: string;
  }>;
  upcoming_payments: Array<{
    description: string;
    amount: number;
    due_date: string;
  }>;
  thirty_day_projection: number;
  last_updated: string;
}

export interface TodoItem {
  id: string;
  title: string;
  status: string;
  assigned_to?: string;
  due_date?: string;
  project?: string;
  category?: string; // Ajouté pour les todos Google Sheets
}

export interface BasecampData {
  todos: TodoItem[];
  projects_count: number;
  completed_today: number;
  last_updated: string;
}

// Types pour les todos Google Sheets
export interface TodosByCategory {
  category: string;
  todos: TodoItem[];
  total_count: number;
  pending_count: number;
  completed_count: number;
}

export interface TodosData {
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

export interface FacebookVideoData {
  id: string;
  title: string;
  thumbnail_url: string;
  video_url: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  published_date: string;
  duration: number;
}

export interface ActionPlanItem {
  id: string;
  title: string;
  assigned_to: string;
  due_date: string;
  priority: TaskPriority;
  status: TaskStatus;
  category: 'today' | 'this_week' | 'upcoming' | 'later';
}

// Configuration et mise à jour
export interface DashboardConfig {
  refresh_intervals: {
    team_availability: number;
    planning: number;
    cash_flow: number;
    todos: number;
    facebook: number;
    kpis: number;
  };
  rotation_settings: {
    planning_duration: number;
    actions_duration: number;
    cash_flow_duration: number;
  };
}

export interface UpdateNotification {
  type: 'team_availability' | 'planning' | 'cash_flow' | 'todos' | 'facebook' | 'kpis';
  data: any;
  timestamp: string;
  source: string;
}

// Hooks et services
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  last_updated: string;
}

export interface DashboardState {
  dashboard1: {
    default_alive: DefaultAliveData | null;
    public_engagement: PublicEngagementData | null;
    fundraising_pipeline: FundraisingPipelineData | null;
    loading: boolean;
    error: string | null;
  };
  dashboard2: {
    team_availability: TeamMember[];
    weekly_planning: WeeklyPlanningData | null;
    cash_flow: CashFlowData | null;
    action_plan: ActionPlanItem[];
    todos: BasecampData | null;
    facebook_video: FacebookVideoData | null;
    loading: boolean;
    error: string | null;
  };
  connection_status: 'connected' | 'disconnected' | 'reconnecting';
  last_global_update: string;
}

// Composants Props
export interface DashboardCardProps {
  title: string;
  icon?: string;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
}

export interface ProgressBarProps {
  progress: number;
  variant?: 'green' | 'orange' | 'red' | 'blue' | 'yellow';
  showLabel?: boolean;
  height?: 'sm' | 'md' | 'lg';
}

export interface StatusIndicatorProps {
  status: Status;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export interface RotatingContentProps {
  views: Array<{
    id: string;
    component: React.ReactNode;
    duration: number;
  }>;
  autoRotate?: boolean;
}

// Utilitaires
export type ColorScheme = {
  primary: string;
  secondary: string;
  success: string;
  warning: string;
  error: string;
};

export interface DateRange {
  start: string;
  end: string;
}

export interface KPITrendPoint {
  date: string;
  value: number;
  label?: string;
}

// Response type for complete Dashboard 2 data
export interface Dashboard2Response {
  team_availability: TeamAvailabilityData;
  weekly_planning: WeeklyPlanningData;
  basecamp_data: BasecampData;
  action_plan: ActionPlanItem[];
  cash_flow: CashFlowData;
  facebook_video: FacebookVideoData | null;
  last_updated: string;
}