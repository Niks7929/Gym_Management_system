import React, { type ReactNode } from 'react';
import { useAuthStore } from '../contexts/authStore';
import { useGymSettingsQuery } from '../api/queries';
import {
  Users, CalendarCheck, CreditCard, Dumbbell,
  Utensils, BarChart3, Building2, Settings, Flame, LogOut,
  UserPlus
} from 'lucide-react';
import { Button } from '../components/ui';
import { ThemeToggle } from '../components/ThemeToggle';

interface NavItem {
  id: string;
  label: string;
  icon: any;
  badge?: string;
}

interface DashboardLayoutProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  onLogout?: () => void;
  children: ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  currentTab,
  onTabChange,
  onLogout,
  children,
}) => {
  const { user, logout } = useAuthStore();
  const { data: settings } = useGymSettingsQuery();
  const role = user?.role || 'member';

  const handleSignOut = () => {
    logout();
    if (onLogout) {
      onLogout();
    } else if (typeof window !== 'undefined') {
      window.history.pushState({}, '', '/');
      window.location.reload();
    }
  };

  const getNavItems = (): NavItem[] => {
    switch (role) {
      case 'admin':
        return [
          { id: 'admin-dashboard', label: 'Executive Analytics', icon: BarChart3 },
          { id: 'admin-enquiries', label: 'Leads & Enquiries', icon: Users },
          { id: 'admin-verifications', label: 'Pending UTR Approvals', icon: CreditCard },
          { id: 'admin-users', label: 'Staff & Members', icon: Users },
          { id: 'admin-plans', label: 'Membership Plans (₹)', icon: Flame },
          { id: 'admin-branches', label: 'Gym Branches', icon: Building2 },
          { id: 'admin-attendance', label: 'Global Attendance', icon: CalendarCheck },
          { id: 'admin-payments', label: 'Revenue & Invoices (₹)', icon: CreditCard },
          { id: 'admin-settings', label: 'Frontend CMS & Settings', icon: Settings },
        ];
      case 'receptionist':
        return [
          { id: 'rec-dashboard', label: 'Front-Desk Overview', icon: BarChart3 },
          { id: 'rec-enquiries', label: 'Leads & Enquiries', icon: Users },
          { id: 'rec-verifications', label: 'Pending UTR Approvals', icon: CreditCard },
          { id: 'rec-onboarding', label: 'Member Onboarding', icon: UserPlus },
          { id: 'rec-attendance', label: 'Fast Check-In', icon: CalendarCheck },
          { id: 'rec-renewals', label: 'Renewals & Expiry', icon: CreditCard },
          { id: 'rec-payments', label: 'Payment Billing (₹)', icon: CreditCard },
        ];
      case 'trainer':
        return [
          { id: 'trainer-dashboard', label: 'Coach Roster', icon: BarChart3 },
          { id: 'trainer-clients', label: 'My Assigned Clients', icon: Users },
          { id: 'trainer-workouts', label: 'Workout Builder', icon: Dumbbell },
          { id: 'trainer-diets', label: 'Nutrition & Diets', icon: Utensils },
          { id: 'trainer-attendance', label: 'Client Attendance', icon: CalendarCheck },
        ];
      case 'member':
      default:
        return [
          { id: 'member-dashboard', label: 'My Fitness Hub', icon: Flame },
          { id: 'member-workout', label: 'Workout Schedule', icon: Dumbbell },
          { id: 'member-diet', label: 'Diet & Nutrition', icon: Utensils },
          { id: 'member-attendance', label: 'My Attendance Logs', icon: CalendarCheck },
          { id: 'member-subscription', label: 'Plan & Invoices (₹)', icon: CreditCard },
        ];
    }
  };

  const navItems = getNavItems();

  const getRoleBadge = (r: string) => {
    switch (r) {
      case 'admin':
        return (
          <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border bg-slate-900 text-white dark:bg-white dark:text-black border-transparent shadow-sm">
            👑 Master Admin
          </span>
        );
      case 'receptionist':
        return (
          <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border bg-slate-100 text-slate-800 dark:bg-zinc-900 dark:text-zinc-200 border-slate-200 dark:border-white/20">
            📋 Front Desk
          </span>
        );
      case 'trainer':
        return (
          <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border bg-slate-100 text-slate-800 dark:bg-zinc-900 dark:text-white border-slate-200 dark:border-white/20">
            🏋️ Master Coach
          </span>
        );
      case 'member':
      default:
        return (
          <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border bg-slate-100 text-slate-800 dark:bg-zinc-900 dark:text-zinc-300 border-slate-200 dark:border-white/15">
            👤 Active Athlete
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#040406] text-slate-900 dark:text-zinc-100 flex flex-col font-sans transition-colors duration-200">
      {/* Main Header */}
      <header className="bg-white/95 dark:bg-[#07070a]/95 backdrop-blur-md border-b border-slate-200 dark:border-white/10 sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
        <button
          onClick={handleSignOut}
          className="flex items-center gap-3 text-left group cursor-pointer"
          title="Exit to Home Page"
        >
          <div className="w-10 h-10 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <Flame className="w-6 h-6 text-current" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-black text-xl tracking-wider text-slate-900 dark:text-white">
                {settings?.gym_name?.split(' ')[0] || 'SETFIT'}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-900 text-slate-700 dark:text-zinc-300 font-mono font-black border border-slate-200 dark:border-white/15 uppercase tracking-wider">
                {settings?.gym_name?.split(' ').slice(1).join(' ') || 'ELITE'}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium">Enterprise Gym Management & RBAC Portal</p>
          </div>
        </button>

        <div className="flex items-center gap-4">
          <div className="hidden md:flex flex-col items-end">
            <div className="flex items-center gap-2">
              <span className="text-sm font-black text-slate-900 dark:text-white">{user?.first_name} {user?.last_name}</span>
              {getRoleBadge(role)}
            </div>
            <span className="text-xs text-slate-500 dark:text-zinc-400 font-mono">{user?.email}</span>
          </div>

          {/* Theme Switcher in Top Bar */}
          <ThemeToggle />

          <Button
            variant="outline"
            size="sm"
            onClick={handleSignOut}
            className="text-xs uppercase font-bold cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sign Out</span>
          </Button>
        </div>
      </header>

      {/* Body container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white dark:bg-[#07070a] border-r border-slate-200 dark:border-white/10 p-4 flex flex-col justify-between hidden md:flex">
          <div className="space-y-1.5">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-zinc-500 px-3 mb-2">
              Navigation Module
            </p>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-black shadow-sm font-black'
                      : 'text-slate-600 dark:text-zinc-400 hover:text-black dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-900/60'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 ${isActive ? 'text-current' : 'text-slate-500 dark:text-zinc-400'}`}
                    />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[10px] bg-slate-200 dark:bg-zinc-800 text-slate-700 dark:text-zinc-200 px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-[#0b0b0f] border border-slate-200 dark:border-white/10 text-xs text-slate-600 dark:text-zinc-400 space-y-1">
            <div className="flex items-center justify-between text-slate-800 dark:text-zinc-200 font-bold">
              <span>Security Engine</span>
              <span className="text-slate-900 dark:text-white font-mono text-[11px] font-black bg-slate-200 dark:bg-zinc-900 px-1.5 py-0.5 rounded border border-slate-300 dark:border-white/15">
                IN-MEMORY JWT
              </span>
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">Zero LocalStorage (XSS Mitigated)</p>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-slate-50 dark:bg-[#040406]">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
