import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './contexts/authStore';
import { HomePage } from './pages/public/HomePage';
import { LoginPage } from './pages/auth/LoginPage';
import { AdminLoginPage } from './pages/auth/AdminLoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardLayout } from './layouts/DashboardLayout';
import { AdminPortal } from './pages/admin/AdminPortal';
import { ReceptionistPortal } from './pages/receptionist/ReceptionistPortal';
import { TrainerPortal } from './pages/trainer/TrainerPortal';
import { MemberPortal } from './pages/member/MemberPortal';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 30, // 30 seconds
    },
  },
});

type PublicView = 'home' | 'login' | 'register' | 'admin-control';

export const AppContent: React.FC = () => {
  const { isAuthenticated, user } = useAuthStore();
  
  // Check if browser URL is pointing to secret admin portal
  const getInitialView = (): PublicView => {
    if (typeof window !== 'undefined') {
      const path = window.location.pathname.toLowerCase();
      if (path === '/setfit-control-portal' || path.includes('control-portal')) {
        return 'admin-control';
      }
      if (path === '/login') return 'login';
      if (path === '/register') return 'register';
    }
    return 'home';
  };

  const [publicView, setPublicView] = useState<PublicView>(getInitialView());
  const [selectedPlanId, setSelectedPlanId] = useState<number | undefined>(undefined);
  const [currentTab, setCurrentTab] = useState<string>('');

  // Synchronize browser history / URL path
  const navigateTo = (view: PublicView, path: string = '/') => {
    setPublicView(view);
    if (typeof window !== 'undefined') {
      window.history.pushState({}, '', path);
    }
  };

  const handleLogoutToHome = () => {
    useAuthStore.getState().logout();
    queryClient.clear();
    navigateTo('home', '/');
  };

  // Listen to browser back/forward buttons - auto-logout when leaving to any public URL
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname.toLowerCase();
      // Auto-logout when navigating back or to public URLs
      useAuthStore.getState().logout();
      queryClient.clear();

      if (path === '/setfit-control-portal' || path.includes('control-portal')) {
        setPublicView('admin-control');
      } else if (path === '/login') {
        setPublicView('login');
      } else if (path === '/register') {
        setPublicView('register');
      } else {
        setPublicView('home');
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Default tab when user role changes
  useEffect(() => {
    if (user?.role === 'admin') setCurrentTab('admin-dashboard');
    else if (user?.role === 'receptionist') setCurrentTab('rec-dashboard');
    else if (user?.role === 'trainer') setCurrentTab('trainer-dashboard');
    else if (user?.role === 'member') setCurrentTab('member-dashboard');
  }, [user?.role]);

  // If user is not logged in, show Public views (Home, Login, Register, Secret Admin Portal)
  if (!isAuthenticated || !user) {
    if (publicView === 'admin-control') {
      return (
        <AdminLoginPage
          onNavigateHome={() => navigateTo('home', '/')}
        />
      );
    }

    if (publicView === 'login') {
      return (
        <LoginPage
          onNavigateRegister={() => navigateTo('register', '/register')}
          onNavigateHome={() => navigateTo('home', '/')}
        />
      );
    }

    if (publicView === 'register') {
      return (
        <RegisterPage
          initialPlanId={selectedPlanId}
          onNavigateLogin={() => navigateTo('login', '/login')}
          onNavigateHome={() => navigateTo('home', '/')}
        />
      );
    }

    return (
      <HomePage
        onNavigateLogin={() => navigateTo('login', '/login')}
        onNavigateRegister={(planId) => {
          setSelectedPlanId(planId);
          navigateTo('register', '/register');
        }}
        onNavigateAdminControl={() => navigateTo('admin-control', '/setfit-control-portal')}
      />
    );
  }

  // If user is authenticated, render Role-Based Protected Dashboard
  return (
    <DashboardLayout
      currentTab={currentTab}
      onTabChange={setCurrentTab}
      onLogout={handleLogoutToHome}
    >
      {user.role === 'admin' && <AdminPortal currentTab={currentTab} />}
      {user.role === 'receptionist' && <ReceptionistPortal currentTab={currentTab} />}
      {user.role === 'trainer' && <TrainerPortal currentTab={currentTab} />}
      {user.role === 'member' && <MemberPortal currentTab={currentTab} />}
    </DashboardLayout>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
