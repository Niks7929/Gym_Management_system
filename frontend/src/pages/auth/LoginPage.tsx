import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../contexts/authStore';
import {
  Flame, Shield, KeyRound, Mail, ArrowLeft,
  CheckCircle2, ClipboardList, Dumbbell, User as UserIcon
} from 'lucide-react';
import { Button, Input, Card } from '../../components/ui';
import { ThemeToggle } from '../../components/ThemeToggle';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(4, 'Password must be at least 4 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

type PublicPortalType = 'member' | 'trainer' | 'receptionist';

interface LoginPageProps {
  onNavigateRegister: () => void;
  onNavigateHome: () => void;
}

const PUBLIC_PORTALS: {
  id: PublicPortalType;
  label: string;
  icon: any;
  tagline: string;
  defaultEmail: string;
}[] = [
  {
    id: 'member',
    label: 'Member',
    icon: UserIcon,
    tagline: 'Access your workout plans, custom diet charts, QR pass & active subscriptions',
    defaultEmail: 'alex.mercer@setfitgym.com',
  },
  {
    id: 'trainer',
    label: 'Trainer',
    icon: Dumbbell,
    tagline: 'Manage assigned clients, build custom workout plans & meal schedules',
    defaultEmail: 'trainer@setfitgym.com',
  },
  {
    id: 'receptionist',
    label: 'Receptionist',
    icon: ClipboardList,
    tagline: 'Front desk check-in, POS invoicing, onboarding & branch lookup',
    defaultEmail: 'receptionist@setfitgym.com',
  },
];

export const LoginPage: React.FC<LoginPageProps> = ({
  onNavigateRegister,
  onNavigateHome,
}) => {
  const { setAuth } = useAuthStore();
  const [selectedPortal, setSelectedPortal] = useState<PublicPortalType>('member');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const activePortal = PUBLIC_PORTALS.find((p) => p.id === selectedPortal) || PUBLIC_PORTALS[0];

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  // Explicitly wipe input fields on mount and when switching portal tabs
  React.useEffect(() => {
    reset({ email: '', password: '' });
    setErrorMessage(null);
  }, [selectedPortal, reset]);

  const handleSelectPortal = (portalId: PublicPortalType) => {
    setSelectedPortal(portalId);
    setErrorMessage(null);
    reset({ email: '', password: '' });
  };

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await apiClient.post('/auth/login', data);
      const { access_token, user } = response.data;
      setAuth(access_token, user);
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Authentication failed. Please verify your email and password.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#040406] flex flex-col justify-center items-center p-4 sm:p-6 relative font-sans transition-colors duration-200">
      <div className="w-full max-w-md z-10 py-6">
        {/* Top bar with Back and Theme Toggle */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onNavigateHome}
            className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Home
          </button>
          <ThemeToggle />
        </div>

        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center mx-auto shadow-sm mb-3">
            <Flame className="w-6 h-6" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-wider text-slate-900 dark:text-white uppercase">
            SETFIT SIGN IN
          </h1>
          <p className="text-xs font-medium text-slate-500 dark:text-zinc-400 mt-1">
            Select your account type to access your portal
          </p>
        </div>

        {/* Clean Simple Role Selector Tabs (Member, Trainer, Receptionist) */}
        <div className="grid grid-cols-3 gap-2 mb-4 p-1.5 rounded-2xl bg-slate-200/80 dark:bg-zinc-900 border border-slate-300 dark:border-white/10">
          {PUBLIC_PORTALS.map((portal) => {
            const Icon = portal.icon;
            const isSelected = selectedPortal === portal.id;
            return (
              <button
                key={portal.id}
                type="button"
                onClick={() => handleSelectPortal(portal.id)}
                className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl font-bold text-xs transition-all duration-150 cursor-pointer ${
                  isSelected
                    ? 'bg-white text-slate-900 dark:bg-white dark:text-black shadow-sm font-black'
                    : 'text-slate-600 dark:text-zinc-400 hover:text-black dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{portal.label}</span>
              </button>
            );
          })}
        </div>

        {/* Auth Card */}
        <Card className="p-6 sm:p-7 border-slate-200 dark:border-white/10">
          <div className="mb-4 text-center">
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              {activePortal.tagline}
            </p>
          </div>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
              <Shield className="w-4 h-4 text-red-500 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" autoComplete="off">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                Email Address
              </label>
              <Input
                type="email"
                placeholder="Enter your registered email"
                autoComplete="off"
                {...register('email')}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-xs text-red-500 mt-1 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5 flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                Password
              </label>
              <Input
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                {...register('password')}
                className={errors.password ? 'border-red-500' : ''}
              />
              {errors.password && (
                <p className="text-xs text-red-500 mt-1 font-medium">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full mt-2 uppercase text-xs font-black tracking-wider"
            >
              Sign In as {activePortal.label}
            </Button>
          </form>

          {/* Registration link */}
          <div className="mt-6 pt-5 border-t border-slate-100 dark:border-white/10 text-center text-xs text-slate-500 dark:text-zinc-400">
            <p>
              Looking to join as a new athlete?{' '}
              <button
                onClick={onNavigateRegister}
                className="text-slate-900 dark:text-white font-black hover:underline cursor-pointer ml-1 uppercase"
              >
                Register & Select Pass
              </button>
            </p>
          </div>
        </Card>

        {/* Security badge footer */}
        <div className="mt-5 text-center text-xs text-slate-500 dark:text-zinc-500 flex items-center justify-center gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-zinc-400" />
          <span>Encrypted In-Memory JWT Authentication (XSS Protected)</span>
        </div>
      </div>
    </div>
  );
};
