import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../contexts/authStore';
import {
  Shield, KeyRound, Mail, ArrowLeft,
  CheckCircle2, Crown, Lock, Terminal
} from 'lucide-react';
import { Button, Input, Card } from '../../components/ui';
import { ThemeToggle } from '../../components/ThemeToggle';

const adminLoginSchema = z.object({
  email: z.string().email('Please enter a valid administrator email'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type AdminLoginFormData = z.infer<typeof adminLoginSchema>;

interface AdminLoginPageProps {
  onNavigateHome: () => void;
}

export const AdminLoginPage: React.FC<AdminLoginPageProps> = ({ onNavigateHome }) => {
  const { setAuth } = useAuthStore();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AdminLoginFormData>({
    resolver: zodResolver(adminLoginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  // Explicitly reset on mount so browser saved password does not prefill
  React.useEffect(() => {
    reset({ email: '', password: '' });
    setErrorMessage(null);
  }, [reset]);

  const onSubmit = async (data: AdminLoginFormData) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await apiClient.post('/auth/login', data);
      const { access_token, user } = response.data;
      
      if (user.role !== 'admin') {
        setErrorMessage('Access Denied: Account lacks Master Administrator authorization.');
        return;
      }
      
      setAuth(access_token, user);
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Authentication failed. Please verify your administrator credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 dark:bg-[#020204] text-white flex flex-col justify-center items-center p-4 sm:p-6 relative font-sans">
      <div className="w-full max-w-md z-10 py-6">
        {/* Top bar with Back and Theme Toggle */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onNavigateHome}
            className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" /> Return to SETFIT
          </button>
          <ThemeToggle />
        </div>

        {/* Security Header */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-white text-black flex items-center justify-center mx-auto shadow-white-btn mb-3">
            <Crown className="w-8 h-8 text-black" />
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-950/60 border border-red-800 text-red-400 text-[10px] font-black uppercase tracking-widest mb-2">
            <Lock className="w-3 h-3" /> RESTRICTED SYSTEM AREA
          </div>
          <h1 className="text-2xl font-black tracking-widest text-white uppercase">
            SETFIT CONTROL PORTAL
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Master administrative console authorization
          </p>
        </div>

        {/* Auth Card */}
        <Card className="p-6 sm:p-8 bg-slate-800/90 dark:bg-[#09090e] border-slate-700 dark:border-white/10 shadow-2xl">
          <div className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-900 dark:bg-black/50 border border-slate-700 dark:border-white/10 mb-5 text-xs text-slate-300">
            <Terminal className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Encrypted endpoint: <strong className="text-white font-mono">/setfit-control-portal</strong></span>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-950/80 border border-red-800 text-red-300 text-xs flex items-center gap-2.5">
              <Shield className="w-4 h-4 text-red-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" autoComplete="off">
            <div>
              <label className="block text-xs font-black uppercase tracking-wider text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                Administrator Email
              </label>
              <Input
                type="email"
                placeholder="admin@setfitgym.com"
                autoComplete="off"
                {...register('email')}
                className="bg-slate-900 dark:bg-[#050508] border-slate-700 text-white placeholder-slate-500"
              />
              {errors.email && (
                <p className="text-xs text-red-400 mt-1 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-xs font-black uppercase tracking-wider text-slate-300 mb-1.5 flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-slate-400" />
                Master Password
              </label>
              <Input
                type="password"
                placeholder="••••••••••••"
                autoComplete="new-password"
                {...register('password')}
                className="bg-slate-900 dark:bg-[#050508] border-slate-700 text-white placeholder-slate-500"
              />
              {errors.password && (
                <p className="text-xs text-red-400 mt-1 font-medium">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full mt-3 uppercase text-xs font-black tracking-wider bg-white text-black hover:bg-slate-200"
            >
              Authorize & Enter Command Center
            </Button>
          </form>
        </Card>

        {/* Footer info */}
        <div className="mt-6 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
          <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" />
          <span>Django bcrypt Password Verification + In-Memory JWT</span>
        </div>
      </div>
    </div>
  );
};
