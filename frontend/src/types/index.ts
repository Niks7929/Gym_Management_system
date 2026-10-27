export type UserRole = 'admin' | 'receptionist' | 'trainer' | 'member';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: UserRole;
  branch_id: number | null;
  branch_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
}

export interface Branch {
  id: number;
  name: string;
  code: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface GymSetting {
  gym_name: string;
  tagline: string;
  announcement_bar: string;
  hero_headline: string;
  hero_subtitle: string;
  hero_badge_text: string;
  hero_cta_primary: string;
  hero_cta_secondary: string;
  theme_accent: string;
  stat_access_hours: string;
  stat_equipment_text: string;
  stat_trainers_count: string;
  stat_members_count: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  currency_symbol: string;
  upi_id?: string;
  date_format: string;
  tax_percentage: number;
  updated_at: string;
}

export interface MembershipPlan {
  id: number;
  name: string;
  duration_type: string;
  duration_days: number;
  price: number;
  description: string;
  features: string[];
  is_active: boolean;
  created_at: string;
}

export interface Subscription {
  id: number;
  member_id: number;
  member_name: string;
  member_email: string;
  member_phone: string;
  plan_id: number;
  plan_name: string;
  plan_price: number;
  start_date: string;
  end_date: string;
  status: 'active' | 'pending_verification' | 'expired' | 'pending' | 'cancelled';
  notes: string;
  days_left: number;
  payment_status?: string;
  utr_number?: string;
  is_verified?: boolean;
  created_at: string;
}

export interface Payment {
  id: number;
  member_id: number;
  member_name: string;
  member_email: string;
  member_phone?: string;
  subscription_id: number | null;
  plan_id?: number | null;
  plan_name: string | null;
  amount: number;
  payment_method: 'cash' | 'card' | 'upi' | 'bank_transfer';
  payment_type: 'initial' | 'renewal' | 'addon';
  status: 'completed' | 'pending_verification' | 'pending' | 'rejected' | 'failed';
  invoice_number: string;
  utr_number?: string;
  upi_vpa?: string;
  rejection_reason?: string;
  verified_at?: string | null;
  transaction_date: string;
  notes: string;
}

export interface Enquiry {
  id: number;
  name: string;
  email?: string | null;
  phone: string;
  preferred_branch_id?: number | null;
  preferred_branch_name?: string | null;
  fitness_goal: string;
  preferred_time?: string | null;
  notes?: string | null;
  message?: string | null;
  status: 'new' | 'contacted' | 'converted' | 'closed' | string;
  created_at: string;
}

export interface Attendance {
  id: number;
  member_id: number;
  member_name: string;
  member_email: string;
  member_phone: string;
  date: string;
  check_in_time: string;
  check_out_time: string | null;
  status: 'present' | 'absent' | 'late';
  notes: string;
  logged_by_name: string | null;
  created_at: string;
}

export interface ExerciseItem {
  name: string;
  sets: string;
  reps: string;
  rest?: string;
  notes?: string;
}

export interface WorkoutDaySchedule {
  day: string;
  exercises: ExerciseItem[];
}

export interface WorkoutPlan {
  id: number;
  trainer_id: number | null;
  trainer_name: string | null;
  member_id: number;
  member_name: string;
  title: string;
  goal: string;
  exercises_schedule: WorkoutDaySchedule[];
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  created_at: string;
}

export interface MealItem {
  time: string;
  meal_name: string;
  items: string;
  calories: number;
  protein: string;
  carbs: string;
  fats: string;
}

export interface DietPlan {
  id: number;
  trainer_id: number | null;
  trainer_name: string | null;
  member_id: number;
  member_name: string;
  title: string;
  daily_calories: number;
  macros: {
    protein?: string;
    carbs?: string;
    fats?: string;
    [key: string]: any;
  };
  meals_schedule: MealItem[];
  guidelines: string;
  is_active: boolean;
  created_at: string;
}

export interface TrainerClient {
  id: number;
  trainer_id: number;
  trainer_name: string;
  member_id: number;
  member_name: string;
  member_email: string;
  member_phone: string;
  start_date: string;
  is_active: boolean;
  notes: string;
  active_plan_name: string;
  days_left_in_membership: number;
}

export interface AdminDashboardStats {
  total_members: number;
  active_members: number;
  expired_members: number;
  total_trainers: number;
  total_receptionists: number;
  today_revenue: number;
  month_revenue: number;
  total_revenue: number;
  today_checkins: number;
  monthly_revenue_trend: {
    month: string;
    revenue: number;
    transactions_count: number;
  }[];
  plan_distribution: {
    plan_name: string;
    member_count: number;
    percentage: number;
  }[];
}

export interface ReceptionistDashboardStats {
  total_members: number;
  active_members: number;
  expiring_soon_7days: number;
  today_checkins: number;
  today_revenue: number;
}

export interface TrainerDashboardStats {
  assigned_clients_count: number;
  active_workouts_count: number;
  active_diets_count: number;
  today_client_checkins: number;
}

export interface MemberDashboardStats {
  has_active_subscription: boolean;
  plan_name: string | null;
  days_left: number;
  expiry_date: string | null;
  total_checkins_this_month: number;
  active_workout_title: string | null;
  active_diet_title: string | null;
  daily_calories: number | null;
}
