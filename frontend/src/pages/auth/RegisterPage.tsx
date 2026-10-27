import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../contexts/authStore';
import { usePlansQuery, useGymSettingsQuery } from '../../api/queries';
import {
  Flame, Shield, ArrowLeft, Mail, KeyRound, User as UserIcon,
  Phone, CheckCircle2, Check, Dumbbell, ClipboardList,
  Award, Clock, Target, DollarSign, Briefcase
} from 'lucide-react';
import { Button, Input, Select, Card } from '../../components/ui';
import { ThemeToggle } from '../../components/ThemeToggle';

const registerSchema = z.object({
  first_name: z.string().min(2, 'First name is required'),
  last_name: z.string().optional(),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().min(7, 'Please enter a valid phone number'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  plan_id: z.string().optional(),
  fitness_goal: z.string().optional(),
  specialization: z.string().optional(),
  experience_years: z.string().optional(),
  certifications: z.string().optional(),
  shift_preference: z.string().optional(),
});

type RegisterFormData = z.infer<typeof registerSchema>;
type RegistrationRole = 'member' | 'trainer' | 'receptionist';

interface RegisterPageProps {
  initialPlanId?: number;
  onNavigateLogin: () => void;
  onNavigateHome: () => void;
}

const FALLBACK_PLANS = [
  {
    id: 1,
    name: 'Iron Starter (Monthly)',
    duration_type: 'monthly',
    duration_days: 30,
    price: 1499,
    description: 'Full gym floor access, locker rooms, mobile workout logs',
    features: ['24/7 Gym Floor Access', 'Locker Room & Showers', 'SETFIT Mobile Workout Logs'],
  },
  {
    id: 2,
    name: 'Titan Quarterly (3 Months)',
    duration_type: 'quarterly',
    duration_days: 90,
    price: 3999,
    description: 'Save 15% + 1 free fitness assessment & diet plan',
    features: ['All Starter Features', 'Free Body Composition Scan', '1 Free Trainer Consultation', 'Sauna & Steam Bath'],
  },
  {
    id: 3,
    name: 'Pro Athlete (6 Months)',
    duration_type: 'half_yearly',
    duration_days: 180,
    price: 6999,
    description: 'Priority personal coaching booking, towel service, and guest passes',
    features: ['All Quarterly Features', 'Free Locker & Towel Service', '2 Guest Passes per Month'],
  },
  {
    id: 4,
    name: 'Rage Elite VIP (Annual)',
    duration_type: 'annual',
    duration_days: 365,
    price: 12999,
    description: 'Best Value! Full VIP access, custom diet & 4 PT sessions',
    features: ['All-Inclusive VIP Pass', 'Unlimited Sauna & Hydrotherapy', 'Personalized Diet Chart', '4 Free 1-on-1 PT Sessions'],
  },
];

const ROLES_INFO: {
  id: RegistrationRole;
  label: string;
  icon: any;
  badge: string;
  tagline: string;
}[] = [
  {
    id: 'member',
    label: 'Athlete Member',
    icon: UserIcon,
    badge: 'Athlete Portal',
    tagline: 'Join SETFIT, pick your training tier, and track your workout routines',
  },
  {
    id: 'trainer',
    label: 'Master Coach',
    icon: Dumbbell,
    badge: 'Trainer Hub',
    tagline: 'Join coaching roster, manage athlete client rosters & prescribe meal charts',
  },
  {
    id: 'receptionist',
    label: 'Front Desk Staff',
    icon: ClipboardList,
    badge: 'Front Desk Portal',
    tagline: 'Staff registration for facility access, member check-ins & payment billing',
  },
];

export const RegisterPage: React.FC<RegisterPageProps> = ({
  initialPlanId,
  onNavigateLogin,
  onNavigateHome,
}) => {
  const { setAuth } = useAuthStore();
  const { data: serverPlans } = usePlansQuery();
  const { data: settings } = useGymSettingsQuery();

  const displayPlans = serverPlans && serverPlans.length > 0 ? serverPlans : FALLBACK_PLANS;

  const [selectedRole, setSelectedRole] = useState<RegistrationRole>('member');
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(initialPlanId || 1);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      password: '',
      plan_id: initialPlanId ? String(initialPlanId) : '1',
      fitness_goal: 'Muscle Building & Hypertrophy',
      specialization: 'Strength & Conditioning',
      experience_years: '3-5 Years Experience',
      certifications: 'ACE / NASM Certified',
      shift_preference: 'Morning Shift (06:00 - 14:00)',
    },
  });

  // Explicitly clear on mount and role tab changes
  useEffect(() => {
    reset({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      password: '',
      plan_id: selectedRole === 'member' ? (initialPlanId ? String(initialPlanId) : '1') : '',
      fitness_goal: 'Muscle Building & Hypertrophy',
      specialization: 'Strength & Conditioning',
      experience_years: '3-5 Years Experience',
      certifications: 'ACE / NASM Certified',
      shift_preference: 'Morning Shift (06:00 - 14:00)',
    });
    setErrorMessage(null);
  }, [selectedRole, initialPlanId, reset]);

  const handleRoleSwitch = (role: RegistrationRole) => {
    setSelectedRole(role);
    setErrorMessage(null);
  };

  const handlePlanSelect = (planId: number | null) => {
    setSelectedPlanId(planId);
    setValue('plan_id', planId ? String(planId) : '');
  };

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const payload: any = {
        first_name: data.first_name,
        last_name: data.last_name || '',
        email: data.email,
        phone: data.phone,
        password: data.password,
        role: selectedRole,
        plan_id: selectedRole === 'member' && selectedPlanId ? Number(selectedPlanId) : undefined,
        fitness_goal: data.fitness_goal,
        specialization: data.specialization,
        experience_years: data.experience_years,
        certifications: data.certifications,
        shift_preference: data.shift_preference,
      };

      const response = await apiClient.post('/auth/register', payload);
      const { access_token, user } = response.data;
      setAuth(access_token, user);
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Registration failed. Please check your information and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const chosenPlan = displayPlans.find((p) => p.id === selectedPlanId);
  const activeRoleConfig = ROLES_INFO.find((r) => r.id === selectedRole) || ROLES_INFO[0];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#040406] flex flex-col justify-center items-center p-4 sm:p-6 relative font-sans transition-colors duration-200">
      <div className="w-full max-w-3xl z-10 py-8">
        {/* Top Navigation & Theme Switcher */}
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
            JOIN {settings?.gym_name?.toUpperCase() || 'SETFIT'}
          </h1>
          <p className="text-xs uppercase tracking-widest font-medium text-slate-500 dark:text-zinc-400 mt-1">
            Role-Based Portal Registration & Onboarding
          </p>
        </div>

        {/* Dynamic Role Switcher Tabs */}
        <div className="grid grid-cols-3 gap-2 mb-6 p-1.5 rounded-2xl bg-slate-200/80 dark:bg-zinc-900 border border-slate-300 dark:border-white/10">
          {ROLES_INFO.map((role) => {
            const Icon = role.icon;
            const isSelected = selectedRole === role.id;
            return (
              <button
                key={role.id}
                type="button"
                onClick={() => handleRoleSwitch(role.id)}
                className={`flex items-center justify-center gap-2 py-3 px-3 rounded-xl font-bold text-xs transition-all duration-150 cursor-pointer ${
                  isSelected
                    ? 'bg-white text-slate-900 dark:bg-white dark:text-black shadow-sm font-black'
                    : 'text-slate-600 dark:text-zinc-400 hover:text-black dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="truncate">{role.label}</span>
              </button>
            );
          })}
        </div>

        {/* Registration Card */}
        <Card className="p-6 sm:p-8 border-slate-200 dark:border-white/10">
          <div className="mb-5 text-center">
            <span className="text-[10px] font-black uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-800 dark:bg-zinc-800 dark:text-zinc-200 border border-slate-200 dark:border-white/10">
              {activeRoleConfig.badge}
            </span>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-2">
              {activeRoleConfig.tagline}
            </p>
          </div>

          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs flex items-center gap-2.5">
              <Shield className="w-4 h-4 text-red-500 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" autoComplete="off">
            {/* Step 1: Personal Account Credentials */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-white/10">
                <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                  1
                </span>
                <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase">
                  {selectedRole === 'member' ? 'Athlete' : selectedRole === 'trainer' ? 'Coach' : 'Staff'} Information
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                    <UserIcon className="w-3.5 h-3.5 text-slate-400" /> First Name *
                  </label>
                  <Input
                    placeholder="Enter first name"
                    autoComplete="off"
                    {...register('first_name')}
                    className={errors.first_name ? 'border-red-500' : ''}
                  />
                  {errors.first_name && (
                    <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.first_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1">
                    Last Name
                  </label>
                  <Input
                    placeholder="Enter last name"
                    autoComplete="off"
                    {...register('last_name')}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                    <Mail className="w-3.5 h-3.5 text-slate-400" /> Email Address *
                  </label>
                  <Input
                    type="email"
                    placeholder="name@example.com"
                    autoComplete="off"
                    {...register('email')}
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && (
                    <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-slate-400" /> Phone Number *
                  </label>
                  <Input
                    placeholder="+91 98765 43210"
                    autoComplete="off"
                    {...register('phone')}
                    className={errors.phone ? 'border-red-500' : ''}
                  />
                  {errors.phone && (
                    <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.phone.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-slate-400" /> Account Password *
                </label>
                <Input
                  type="password"
                  placeholder="Minimum 6 characters"
                  autoComplete="new-password"
                  {...register('password')}
                  className={errors.password ? 'border-red-500' : ''}
                />
                {errors.password && (
                  <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.password.message}</p>
                )}
              </div>
            </div>

            {/* Step 2: Role-Specific Professional / Profile Configuration */}

            {/* A. MEMBER SPECIFIC SECTION */}
            {selectedRole === 'member' && (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-white/10">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                    2
                  </span>
                  <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase flex items-center gap-1.5">
                    <Target className="w-3.5 h-3.5 text-slate-500" /> Training Goals & Profile
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1">
                      Primary Fitness Goal
                    </label>
                    <Select {...register('fitness_goal')}>
                      <option value="Muscle Building & Hypertrophy">Muscle Building & Hypertrophy</option>
                      <option value="Fat Loss & Body Recomposition">Fat Loss & Body Recomposition</option>
                      <option value="Strength & Powerlifting">Strength & Powerlifting</option>
                      <option value="Athletic Performance & Speed">Athletic Performance & Speed</option>
                      <option value="General Health & Mobility">General Health & Mobility</option>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1">
                      Current Fitness Experience
                    </label>
                    <Select {...register('experience_years')}>
                      <option value="Beginner (0-1 Years)">Beginner (0-1 Years)</option>
                      <option value="Intermediate (1-3 Years)">Intermediate (1-3 Years)</option>
                      <option value="Advanced Athlete (3+ Years)">Advanced Athlete (3+ Years)</option>
                    </Select>
                  </div>
                </div>

                {/* Membership Pass Tier Selector in ₹ */}
                <div className="space-y-3 pt-3">
                  <div className="flex items-center justify-between pb-1.5">
                    <label className="text-xs font-black text-slate-900 dark:text-white tracking-wider uppercase">
                      Select Membership Pass (₹ / INR)
                    </label>
                    {selectedPlanId && (
                      <button
                        type="button"
                        onClick={() => handlePlanSelect(null)}
                        className="text-[11px] text-slate-500 dark:text-zinc-400 hover:text-black dark:hover:text-white cursor-pointer underline uppercase font-bold"
                      >
                        Clear Pass (Pay at Desk)
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {displayPlans.map((plan) => {
                      const isSelected = selectedPlanId === plan.id;
                      const isAnnual = plan.name.toLowerCase().includes('annual') || plan.name.toLowerCase().includes('titan');
                      return (
                        <div
                          key={plan.id}
                          onClick={() => handlePlanSelect(plan.id)}
                          className={`relative flex flex-col justify-between p-3.5 rounded-2xl border transition-all duration-150 cursor-pointer ${
                            isSelected
                              ? 'bg-slate-900 text-white dark:bg-white dark:text-black border-slate-900 dark:border-white shadow-md scale-[1.01]'
                              : 'bg-slate-50 dark:bg-[#09090d] border-slate-200 dark:border-white/10 hover:border-slate-400 dark:hover:border-white/30 text-slate-900 dark:text-white'
                          }`}
                        >
                          {isAnnual && (
                            <div
                              className={`absolute -top-2.5 right-3 px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider ${
                                isSelected
                                  ? 'bg-white text-slate-900 dark:bg-black dark:text-white'
                                  : 'bg-slate-900 text-white dark:bg-white dark:text-black'
                              }`}
                            >
                              Best Value
                            </div>
                          )}

                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <span className={`text-[10px] font-black uppercase font-mono ${isSelected ? 'text-slate-300 dark:text-zinc-700' : 'text-slate-500 dark:text-zinc-400'}`}>
                                {plan.duration_type}
                              </span>
                              <div className={`w-3.5 h-3.5 rounded-full flex items-center justify-center border ${isSelected ? 'bg-white text-slate-900 dark:bg-black dark:text-white border-transparent' : 'border-slate-300 dark:border-zinc-700'}`}>
                                {isSelected && <Check className="w-2.5 h-2.5" />}
                              </div>
                            </div>

                            <h4 className="text-xs font-black uppercase">{plan.name}</h4>
                            <div className="my-1.5">
                              <span className="text-xl font-black font-mono">₹{plan.price.toLocaleString('en-IN')}</span>
                              <span className={`text-[10px] ${isSelected ? 'text-slate-300 dark:text-zinc-700' : 'text-slate-500 dark:text-zinc-400'}`}>
                                {' '}/ {plan.duration_days}d
                              </span>
                            </div>
                          </div>

                          <div className={`mt-2 pt-2 border-t space-y-1 ${isSelected ? 'border-white/20 dark:border-black/10' : 'border-slate-200 dark:border-white/10'}`}>
                            {plan.features?.slice(0, 2).map((feat: string, i: number) => (
                              <div key={i} className="flex items-center gap-1 text-[9px]">
                                <CheckCircle2 className={`w-3 h-3 shrink-0 ${isSelected ? 'text-white dark:text-black' : 'text-emerald-600 dark:text-white'}`} />
                                <span className="truncate font-medium">{feat}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* B. TRAINER / COACH SPECIFIC SECTION */}
            {selectedRole === 'trainer' && (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-white/10">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                    2
                  </span>
                  <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-slate-500" /> Coaching Qualifications & Specialization
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <Target className="w-3.5 h-3.5 text-slate-400" /> Coaching Specialization
                    </label>
                    <Select {...register('specialization')}>
                      <option value="Strength & Conditioning">Strength & Conditioning</option>
                      <option value="Hypertrophy & Bodybuilding">Hypertrophy & Bodybuilding</option>
                      <option value="Functional & CrossFit">Functional & CrossFit</option>
                      <option value="Weight Loss & Metabolic Conditioning">Weight Loss & Metabolic Conditioning</option>
                      <option value="Mobility & Injury Rehabilitation">Mobility & Injury Rehabilitation</option>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400" /> Coaching Experience
                    </label>
                    <Select {...register('experience_years')}>
                      <option value="1-2 Years Professional Coaching">1-2 Years Professional Coaching</option>
                      <option value="3-5 Years Experienced Coach">3-5 Years Experienced Coach</option>
                      <option value="5-10 Years Senior Coach">5-10 Years Senior Coach</option>
                      <option value="10+ Years Master Trainer">10+ Years Master Trainer</option>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <Award className="w-3.5 h-3.5 text-slate-400" /> Certifications & Accreditations
                    </label>
                    <Input
                      placeholder="e.g. ACE / NASM / CSCS / ISSA / CPR"
                      autoComplete="off"
                      {...register('certifications')}
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <DollarSign className="w-3.5 h-3.5 text-slate-400" /> Hourly Rate (₹ / hr)
                    </label>
                    <Select {...register('fitness_goal')}>
                      <option value="₹800 / hr (Tier 1 Coach)">₹800 / hr (Tier 1 Coach)</option>
                      <option value="₹1,200 / hr (Senior Coach)">₹1,200 / hr (Senior Coach)</option>
                      <option value="₹1,800 / hr (Master Coach)">₹1,800 / hr (Master Coach)</option>
                      <option value="₹2,500 / hr (Elite Specialist)">₹2,500 / hr (Elite Specialist)</option>
                    </Select>
                  </div>
                </div>
              </div>
            )}

            {/* C. RECEPTIONIST SPECIFIC SECTION */}
            {selectedRole === 'receptionist' && (
              <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-white/10">
                  <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                    2
                  </span>
                  <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-slate-500" /> Front Desk Operations & Availability
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" /> Shift Preference
                    </label>
                    <Select {...register('shift_preference')}>
                      <option value="Morning Shift (06:00 - 14:00)">Morning Shift (06:00 - 14:00)</option>
                      <option value="Evening Shift (14:00 - 22:00)">Evening Shift (14:00 - 22:00)</option>
                      <option value="Full Flexible Shift Rotation">Full Flexible Shift Rotation</option>
                    </Select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1 flex items-center gap-1.5">
                      <Briefcase className="w-3.5 h-3.5 text-slate-400" /> Customer Service Experience
                    </label>
                    <Select {...register('experience_years')}>
                      <option value="Entry Level / Fast Learner">Entry Level / Fast Learner</option>
                      <option value="1-3 Years Front Desk Experience">1-3 Years Front Desk Experience</option>
                      <option value="3+ Years Hospitality / Gym Management">3+ Years Hospitality / Gym Management</option>
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1">
                    Primary Operational Skills
                  </label>
                  <Select {...register('specialization')}>
                    <option value="Member Onboarding & POS Invoicing">Member Onboarding & POS Invoicing</option>
                    <option value="Attendance Check-In & Facility Access">Attendance Check-In & Facility Access</option>
                    <option value="Customer Relations & Renewal Recovery">Customer Relations & Renewal Recovery</option>
                  </Select>
                </div>
              </div>
            )}

            {/* Total Summary for Members */}
            {selectedRole === 'member' && (
              <div className="p-4 rounded-2xl bg-slate-100 dark:bg-zinc-900/80 border border-slate-200 dark:border-white/10 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 dark:text-zinc-400 uppercase font-bold tracking-wider">Selected Pass:</span>
                  <span className="font-black text-slate-900 dark:text-white uppercase font-mono">
                    {chosenPlan ? `${chosenPlan.name} (₹${chosenPlan.price.toLocaleString('en-IN')})` : 'Free Registration / Pay at Front Desk'}
                  </span>
                </div>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full uppercase text-xs font-black tracking-widest py-4 cursor-pointer"
            >
              {selectedRole === 'member'
                ? 'Complete Athlete Registration & Enter Member Portal'
                : selectedRole === 'trainer'
                ? 'Complete Coach Registration & Enter Trainer Portal'
                : 'Complete Staff Registration & Enter Front Desk Portal'}
            </Button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-500 dark:text-zinc-400 pt-4 border-t border-slate-100 dark:border-white/10">
            Already have an active account?{' '}
            <button
              onClick={onNavigateLogin}
              className="text-slate-900 dark:text-white font-black hover:underline cursor-pointer uppercase ml-1"
            >
              Sign In to Your Portal
            </button>
          </div>
        </Card>
      </div>
    </div>
  );
};


