import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import type {
  User, Branch, GymSetting, MembershipPlan, Subscription,
  Payment, Attendance, WorkoutPlan, DietPlan, TrainerClient,
  AdminDashboardStats, ReceptionistDashboardStats, TrainerDashboardStats, MemberDashboardStats
} from '../types';

// --- Auth & Users ---
export const useCurrentUserQuery = () =>
  useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const { data } = await apiClient.get<User>('/auth/me');
      return data;
    },
  });

export const useUsersQuery = (params?: { role?: string; search?: string; branch_id?: number }) =>
  useQuery({
    queryKey: ['users', params],
    queryFn: async () => {
      const { data } = await apiClient.get<User[]>('/auth/users', { params });
      return data;
    },
  });

export const useCreateUserMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<User>('/auth/users', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
    },
  });
};

export const useUpdateUserMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const res = await apiClient.put<User>(`/auth/users/${id}`, data);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
    },
  });
};

export const useDeleteUserMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.delete(`/auth/users/${id}`);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
    },
  });
};

// --- Branches & Settings ---
export const useBranchesQuery = () =>
  useQuery({
    queryKey: ['branches'],
    queryFn: async () => {
      const { data } = await apiClient.get<Branch[]>('/branches');
      return data;
    },
  });

export const useCreateBranchMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<Branch>('/branches', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branches'] }),
  });
};

export const useUpdateBranchMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const res = await apiClient.put<Branch>(`/branches/${id}`, data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branches'] }),
  });
};

export const useDeleteBranchMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.delete(`/branches/${id}`);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['branches'] }),
  });
};

export const useGymSettingsQuery = () =>
  useQuery({
    queryKey: ['gymSettings'],
    queryFn: async () => {
      const { data } = await apiClient.get<GymSetting>('/settings');
      return data;
    },
  });

export const useUpdateGymSettingsMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<GymSetting>) => {
      const { data } = await apiClient.put<GymSetting>('/settings', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['gymSettings'] }),
  });
};

// --- Plans & Subscriptions ---
export const usePlansQuery = () =>
  useQuery({
    queryKey: ['plans'],
    queryFn: async () => {
      const { data } = await apiClient.get<MembershipPlan[]>('/plans');
      return data;
    },
  });

export const useCreatePlanMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<MembershipPlan>('/plans', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plans'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
    },
  });
};

export const useUpdatePlanMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const res = await apiClient.put<MembershipPlan>(`/plans/${id}`, data);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plans'] }),
  });
};

export const useDeletePlanMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.delete(`/plans/${id}`);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plans'] }),
  });
};

export const useSubscriptionsQuery = (params?: { status?: string; expiring_soon_days?: number; search?: string; member_id?: number }) =>
  useQuery({
    queryKey: ['subscriptions', params],
    queryFn: async () => {
      const { data } = await apiClient.get<Subscription[]>('/subscriptions', { params });
      return data;
    },
  });

export const useMyActiveSubscriptionQuery = () =>
  useQuery({
    queryKey: ['myActiveSubscription'],
    queryFn: async () => {
      const { data } = await apiClient.get<Subscription | null>('/subscriptions/my-active');
      return data;
    },
  });

export const useRenewSubscriptionMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: any }) => {
      const res = await apiClient.post<Subscription>(`/subscriptions/renew/${id}`, data);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

export const useOnboardMemberMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post('/onboard-member', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['users'] });
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

// --- Payments ---
export const usePaymentsQuery = (params?: { member_id?: number; status?: string; payment_type?: string }) =>
  useQuery({
    queryKey: ['payments', params],
    queryFn: async () => {
      const { data } = await apiClient.get<Payment[]>('/payments', { params });
      return data;
    },
  });

export const useCreatePaymentMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<Payment>('/payments', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

// --- Attendance ---
export const useAttendancesQuery = (params?: { date_filter?: string; member_id?: number; search?: string }) =>
  useQuery({
    queryKey: ['attendances', params],
    queryFn: async () => {
      const { data } = await apiClient.get<Attendance[]>('/attendances', { params });
      return data;
    },
  });

export const useTodayAttendanceSummaryQuery = () =>
  useQuery({
    queryKey: ['todayAttendanceSummary'],
    queryFn: async () => {
      const { data } = await apiClient.get('/attendances/today-summary');
      return data;
    },
  });

export const useCheckInMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<Attendance>('/attendances/check-in', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['attendances'] });
      qc.invalidateQueries({ queryKey: ['todayAttendanceSummary'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

export const useCheckOutMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { attendance_id: number; check_out_time?: string }) => {
      const { data } = await apiClient.post<Attendance>('/attendances/check-out', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['attendances'] });
    },
  });
};

// --- Training, Workouts & Diets ---
export const useTrainerClientsQuery = (trainerId?: number) =>
  useQuery({
    queryKey: ['trainerClients', trainerId],
    queryFn: async () => {
      const { data } = await apiClient.get<TrainerClient[]>('/clients', { params: { trainer_id: trainerId } });
      return data;
    },
  });

export const useAssignClientMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { trainer_id: number; member_id: number; notes?: string }) => {
      const { data } = await apiClient.post('/clients/assign', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['trainerClients'] });
    },
  });
};

export const useWorkoutsQuery = (memberId?: number) =>
  useQuery({
    queryKey: ['workouts', memberId],
    queryFn: async () => {
      const { data } = await apiClient.get<WorkoutPlan[]>('/workouts', { params: { member_id: memberId } });
      return data;
    },
  });

export const useMyActiveWorkoutQuery = () =>
  useQuery({
    queryKey: ['myActiveWorkout'],
    queryFn: async () => {
      const { data } = await apiClient.get<WorkoutPlan | null>('/workouts/my-active');
      return data;
    },
  });

export const useCreateWorkoutMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<WorkoutPlan>('/workouts', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['workouts'] });
      qc.invalidateQueries({ queryKey: ['trainerDashboardStats'] });
    },
  });
};

export const useDietsQuery = (memberId?: number) =>
  useQuery({
    queryKey: ['diets', memberId],
    queryFn: async () => {
      const { data } = await apiClient.get<DietPlan[]>('/diets', { params: { member_id: memberId } });
      return data;
    },
  });

export const useMyActiveDietQuery = () =>
  useQuery({
    queryKey: ['myActiveDiet'],
    queryFn: async () => {
      const { data } = await apiClient.get<DietPlan | null>('/diets/my-active');
      return data;
    },
  });

export const useCreateDietMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: any) => {
      const { data } = await apiClient.post<DietPlan>('/diets', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['diets'] });
      qc.invalidateQueries({ queryKey: ['trainerDashboardStats'] });
    },
  });
};

// --- Analytics ---
export const useAdminAnalyticsQuery = () =>
  useQuery({
    queryKey: ['adminAnalytics'],
    queryFn: async () => {
      const { data } = await apiClient.get<AdminDashboardStats>('/analytics/admin');
      return data;
    },
  });

export const useReceptionistAnalyticsQuery = () =>
  useQuery({
    queryKey: ['receptionistAnalytics'],
    queryFn: async () => {
      const { data } = await apiClient.get<ReceptionistDashboardStats>('/analytics/receptionist');
      return data;
    },
  });

export const useTrainerAnalyticsQuery = () =>
  useQuery({
    queryKey: ['trainerAnalytics'],
    queryFn: async () => {
      const { data } = await apiClient.get<TrainerDashboardStats>('/analytics/trainer');
      return data;
    },
  });

export const useMemberAnalyticsQuery = () =>
  useQuery({
    queryKey: ['memberAnalytics'],
    queryFn: async () => {
      const { data } = await apiClient.get<MemberDashboardStats>('/analytics/member');
      return data;
    },
  });

// --- UTR Submission & Payment Verifications ---
export const usePendingVerificationsQuery = () =>
  useQuery({
    queryKey: ['pendingVerifications'],
    queryFn: async () => {
      const { data } = await apiClient.get<Payment[]>('/payments/pending-verifications');
      return data;
    },
    refetchInterval: 15000, // Auto-refresh pending queue every 15s
  });

export const useSubmitUTRMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { plan_id: number; utr_number: string; upi_vpa?: string; notes?: string }) => {
      const { data } = await apiClient.post<Payment>('/payments/submit-utr', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['myActiveSubscription'] });
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['pendingVerifications'] });
      qc.invalidateQueries({ queryKey: ['memberAnalytics'] });
    },
  });
};

export const useVerifyPaymentMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ paymentId, notes }: { paymentId: number; notes?: string }) => {
      const { data } = await apiClient.post<Payment>(`/payments/verify/${paymentId}`, { notes });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pendingVerifications'] });
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

export const useRejectPaymentMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ paymentId, reason }: { paymentId: number; reason: string }) => {
      const { data } = await apiClient.post<Payment>(`/payments/reject/${paymentId}`, { reason });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pendingVerifications'] });
      qc.invalidateQueries({ queryKey: ['payments'] });
      qc.invalidateQueries({ queryKey: ['subscriptions'] });
      qc.invalidateQueries({ queryKey: ['adminAnalytics'] });
      qc.invalidateQueries({ queryKey: ['receptionistAnalytics'] });
    },
  });
};

// --- Enquiries & Lead Management ---
export const useEnquiriesQuery = (status?: string) =>
  useQuery({
    queryKey: ['enquiries', status],
    queryFn: async () => {
      const { data } = await apiClient.get<any[]>('/enquiries', { params: { status } });
      return data;
    },
    refetchInterval: 20000,
  });

export const useCreateEnquiryMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: {
      name: string;
      phone: string;
      email?: string;
      preferred_branch_id?: number;
      fitness_goal?: string;
      preferred_time?: string;
      notes?: string;
      message?: string;
    }) => {
      const { data } = await apiClient.post('/enquiries', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['enquiries'] });
    },
  });
};

export const useUpdateEnquiryStatusMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status, notes }: { id: number; status: string; notes?: string }) => {
      const { data } = await apiClient.patch(`/enquiries/${id}`, { status, notes });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['enquiries'] });
    },
  });
};

