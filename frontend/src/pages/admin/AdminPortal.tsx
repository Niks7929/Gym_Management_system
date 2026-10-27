import React, { useState, useEffect } from 'react';
import {
  useAdminAnalyticsQuery, useUsersQuery, useCreateUserMutation,
  useDeleteUserMutation, usePlansQuery, useCreatePlanMutation,
  useBranchesQuery, useCreateBranchMutation, useGymSettingsQuery,
  useUpdateGymSettingsMutation, usePaymentsQuery, useAttendancesQuery,
  usePendingVerificationsQuery, useVerifyPaymentMutation, useRejectPaymentMutation,
  useEnquiriesQuery, useUpdateEnquiryStatusMutation
} from '../../api/queries';
import {
  Users, DollarSign, CalendarCheck, Flame, Building2,
  Plus, Trash2, CheckCircle, AlertCircle, Search, LayoutTemplate,
  Globe, Sparkles, Palette, MessageSquare, XCircle,
  CheckCircle2, ShieldCheck, RefreshCw
} from 'lucide-react';
import {
  Card, CardHeader, CardTitle, CardContent, StatCard,
  Button, Badge, Modal, Input, Select
} from '../../components/ui';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface AdminPortalProps {
  currentTab: string;
}

export const AdminPortal: React.FC<AdminPortalProps> = ({ currentTab }) => {
  // Queries
  const { data: stats } = useAdminAnalyticsQuery();
  const { data: users } = useUsersQuery();
  const { data: plans } = usePlansQuery();
  const { data: branches } = useBranchesQuery();
  const { data: settings } = useGymSettingsQuery();
  const { data: payments } = usePaymentsQuery();
  const { data: attendances } = useAttendancesQuery();
  const { data: pendingVerifications, refetch: refetchPending } = usePendingVerificationsQuery();
  const { data: enquiries, refetch: refetchEnquiries } = useEnquiriesQuery();

  // Mutations
  const createUserMutation = useCreateUserMutation();
  const deleteUserMutation = useDeleteUserMutation();
  const createPlanMutation = useCreatePlanMutation();
  const createBranchMutation = useCreateBranchMutation();
  const updateSettingsMutation = useUpdateGymSettingsMutation();
  const verifyPaymentMutation = useVerifyPaymentMutation();
  const rejectPaymentMutation = useRejectPaymentMutation();
  const updateEnquiryStatusMutation = useUpdateEnquiryStatusMutation();

  // Modal States
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [isBranchModalOpen, setIsBranchModalOpen] = useState(false);
  const [rejectingPaymentId, setRejectingPaymentId] = useState<number | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [adminNotice, setAdminNotice] = useState<string | null>(null);

  // Filter States
  const [userRoleFilter, setUserRoleFilter] = useState('all');
  const [userSearch, setUserSearch] = useState('');
  const [enquiryFilter, setEnquiryFilter] = useState('all');
  const [enquirySearch, setEnquirySearch] = useState('');

  // Form States
  const [newUser, setNewUser] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: 'Password@2026',
    role: 'member',
    branch_id: '',
  });

  const [newPlan, setNewPlan] = useState({
    name: '',
    duration_type: 'monthly',
    duration_days: 30,
    price: 49,
    description: '',
    featuresStr: 'Gym Floor Access, Showers',
  });

  const [newBranch, setNewBranch] = useState({
    name: '',
    code: '',
    address: '',
    city: '',
    phone: '',
    email: '',
  });

  const [settingsForm, setSettingsForm] = useState({
    gym_name: '',
    tagline: '',
    announcement_bar: '',
    hero_headline: '',
    hero_subtitle: '',
    hero_badge_text: '',
    hero_cta_primary: '',
    hero_cta_secondary: '',
    theme_accent: 'crimson',
    stat_access_hours: '24/7',
    stat_equipment_text: '100% Olympic',
    stat_trainers_count: '15+',
    stat_members_count: '5,000+',
    contact_email: '',
    contact_phone: '',
    address: '',
    currency_symbol: '₹',
    date_format: 'YYYY-MM-DD',
    tax_percentage: 5.0,
  });

  useEffect(() => {
    if (settings) {
      setSettingsForm({
        gym_name: settings.gym_name || 'SETFIT Dark Rage Elite Fitness',
        tagline: settings.tagline || 'Forged in Iron. Powered by Relentless Discipline.',
        announcement_bar: settings.announcement_bar || '⚡ NEW MEMBER SPECIAL: Sign up today & receive 1 Free 1-on-1 Fitness Assessment!',
        hero_headline: settings.hero_headline || 'UNLEASH YOUR INNER TITAN',
        hero_subtitle: settings.hero_subtitle || 'Welcome to SETFIT DARK RAGE — the premier high-performance strength and conditioning fitness facility.',
        hero_badge_text: settings.hero_badge_text || 'Forged in Iron. Powered by Relentless Discipline.',
        hero_cta_primary: settings.hero_cta_primary || 'Claim Membership Pass',
        hero_cta_secondary: settings.hero_cta_secondary || 'Member Portal Login',
        theme_accent: settings.theme_accent || 'crimson',
        stat_access_hours: settings.stat_access_hours || '24/7',
        stat_equipment_text: settings.stat_equipment_text || '100% Olympic',
        stat_trainers_count: settings.stat_trainers_count || '15+',
        stat_members_count: settings.stat_members_count || '5,000+',
        contact_email: settings.contact_email || 'contact@setfitgym.com',
        contact_phone: settings.contact_phone || '+1 (800) 555-IRON',
        address: settings.address || '777 Titan Way, Iron District, Metropolis',
        currency_symbol: settings.currency_symbol || '₹',
        date_format: settings.date_format || 'YYYY-MM-DD',
        tax_percentage: settings.tax_percentage || 5.0,
      });
    }
  }, [settings]);

  const [savedSuccess, setSavedSuccess] = useState(false);

  // Handlers
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    await createUserMutation.mutateAsync({
      ...newUser,
      branch_id: newUser.branch_id ? Number(newUser.branch_id) : undefined,
    });
    setIsUserModalOpen(false);
    setNewUser({
      first_name: '', last_name: '', email: '', phone: '',
      password: 'Password@2026', role: 'member', branch_id: '',
    });
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    const features = newPlan.featuresStr.split(',').map((f) => f.trim()).filter(Boolean);
    await createPlanMutation.mutateAsync({
      name: newPlan.name,
      duration_type: newPlan.duration_type,
      duration_days: Number(newPlan.duration_days),
      price: Number(newPlan.price),
      description: newPlan.description,
      features,
    });
    setIsPlanModalOpen(false);
    setNewPlan({
      name: '', duration_type: 'monthly', duration_days: 30,
      price: 49, description: '', featuresStr: 'Gym Floor Access, Showers',
    });
  };

  const handleCreateBranch = async (e: React.FormEvent) => {
    e.preventDefault();
    await createBranchMutation.mutateAsync(newBranch);
    setIsBranchModalOpen(false);
    setNewBranch({ name: '', code: '', address: '', city: '', phone: '', email: '' });
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateSettingsMutation.mutateAsync(settingsForm);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  const handleVerifyUTR = async (paymentId: number, memberName: string) => {
    try {
      await verifyPaymentMutation.mutateAsync({ paymentId });
      setAdminNotice(`Successfully verified payment and activated membership for ${memberName}!`);
      setTimeout(() => setAdminNotice(null), 5000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to verify payment');
    }
  };

  const handleRejectUTR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rejectingPaymentId) return;
    try {
      await rejectPaymentMutation.mutateAsync({
        paymentId: rejectingPaymentId,
        reason: rejectionReason || 'Invalid UTR reference number or payment not received',
      });
      setRejectingPaymentId(null);
      setRejectionReason('');
      setAdminNotice('Payment verification rejected. Member notified to submit valid reference.');
      setTimeout(() => setAdminNotice(null), 5000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reject payment');
    }
  };

  const handleUpdateEnquiryStatus = async (enquiryId: number, status: string) => {
    try {
      await updateEnquiryStatusMutation.mutateAsync({ id: enquiryId, status });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update enquiry status');
    }
  };

  const filteredUsers = users?.filter((u) => {
    const matchesRole = userRoleFilter === 'all' || u.role === userRoleFilter;
    const matchesSearch =
      userSearch === '' ||
      `${u.first_name} ${u.last_name} ${u.email} ${u.phone}`.toLowerCase().includes(userSearch.toLowerCase());
    return matchesRole && matchesSearch;
  });

  const filteredEnquiries = enquiries?.filter((enq) => {
    const matchesStatus = enquiryFilter === 'all' || enq.status === enquiryFilter;
    const matchesSearch =
      enquirySearch === '' ||
      `${enq.name} ${enq.phone} ${enq.email || ''} ${enq.fitness_goal}`.toLowerCase().includes(enquirySearch.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {adminNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-sm flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span className="font-bold">{adminNotice}</span>
          </div>
          <button
            onClick={() => setAdminNotice(null)}
            className="text-emerald-400 hover:text-white font-bold text-xs uppercase cursor-pointer"
          >
            ✕ Dismiss
          </button>
        </div>
      )}

      {/* 1. EXECUTIVE ANALYTICS TAB */}
      {(currentTab === 'admin-dashboard' || !currentTab) && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
                <span>Executive Command Center</span>
                <Badge variant="rage">Admin</Badge>
              </h1>
              <p className="text-xs text-zinc-400 mt-1">Real-time revenue metrics, memberships status, and facility utilization</p>
            </div>
          </div>

          {/* Key KPI Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Revenue"
              value={`₹${(stats?.total_revenue || 0).toLocaleString('en-IN')}`}
              subtitle={`₹${(stats?.month_revenue || 0).toLocaleString('en-IN')} this month`}
              icon={DollarSign}
              accent="rage"
              trend="+18.4% vs last month"
            />
            <StatCard
              title="Active Memberships"
              value={stats?.active_members || 0}
              subtitle={`${stats?.expired_members || 0} expired memberships`}
              icon={Users}
              accent="emerald"
            />
            <StatCard
              title="Daily Attendance"
              value={stats?.today_checkins || 0}
              subtitle="Check-ins recorded today"
              icon={CalendarCheck}
              accent="blue"
            />
            <StatCard
              title="Active Staff"
              value={(stats?.total_trainers || 0) + (stats?.total_receptionists || 0)}
              subtitle={`${stats?.total_trainers || 0} Trainers • ${stats?.total_receptionists || 0} Reception`}
              icon={Flame}
              accent="amber"
            />
          </div>

          {/* Revenue Trend Chart & Plan Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>6-Month Revenue Analytics</CardTitle>
                  <p className="text-xs text-zinc-400">Monthly financial gross intake</p>
                </div>
                <Badge variant="rage">Financial Gross</Badge>
              </CardHeader>
              <CardContent className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats?.monthly_revenue_trend || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#272733" opacity={0.5} />
                    <XAxis dataKey="month" stroke="#71717a" fontSize={11} />
                    <YAxis stroke="#71717a" fontSize={11} tickFormatter={(val) => `₹${val}`} />
                    <Tooltip
                      contentStyle={{ background: '#121217', borderColor: '#3f3f46', borderRadius: '8px', color: '#fff' }}
                      formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Revenue']}
                    />
                    <Bar dataKey="revenue" fill="#ffffff" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Plan Breakdown</CardTitle>
                <p className="text-xs text-zinc-400">Distribution of active packages</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats?.plan_distribution?.map((item, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-zinc-200">{item.plan_name}</span>
                      <span className="text-zinc-400 font-mono">{item.member_count} ({item.percentage}%)</span>
                    </div>
                    <div className="w-full bg-zinc-900 rounded-full h-2 overflow-hidden border border-zinc-800">
                      <div
                        className="bg-red-600 h-full rounded-full transition-all duration-500"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* 2. USERS & STAFF MANAGEMENT TAB */}
      {currentTab === 'admin-users' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Staff & Member Governance</h2>
              <p className="text-xs text-zinc-400">Manage user accounts, credentials, and role permissions</p>
            </div>
            <Button onClick={() => setIsUserModalOpen(true)} variant="rage">
              <Plus className="w-4 h-4" /> Add New User
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row items-center gap-3 bg-[#111116] p-3 rounded-xl border border-zinc-800">
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
              <Input
                placeholder="Search by name, email or phone..."
                value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Select value={userRoleFilter} onChange={(e) => setUserRoleFilter(e.target.value)}>
                <option value="all">All Roles</option>
                <option value="admin">Admin</option>
                <option value="receptionist">Receptionist</option>
                <option value="trainer">Trainer</option>
                <option value="member">Member</option>
              </Select>
            </div>
          </div>

          {/* Users Table */}
          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Branch</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {filteredUsers?.map((u) => (
                  <tr key={u.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-bold text-white">{u.first_name} {u.last_name}</div>
                      <div className="text-[11px] text-zinc-500 font-mono">{u.email}</div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={u.role === 'admin' ? 'rage' : u.role === 'receptionist' ? 'purple' : u.role === 'trainer' ? 'warning' : 'success'}>
                        {u.role}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-zinc-300">{u.branch_name || 'Global / All Branches'}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{u.phone || '—'}</td>
                    <td className="px-4 py-3">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                          <CheckCircle className="w-3.5 h-3.5" /> Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-medium">
                          <AlertCircle className="w-3.5 h-3.5" /> Deactivated
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {u.role !== 'admin' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteUserMutation.mutate(u.id)}
                          className="text-zinc-500 hover:text-rose-400 hover:bg-rose-950/30 cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 3. MEMBERSHIP PLANS TAB */}
      {currentTab === 'admin-plans' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Membership Packages & Pricing</h2>
              <p className="text-xs text-zinc-400">Configure tier durations, perks, and pricing models</p>
            </div>
            <Button onClick={() => setIsPlanModalOpen(true)} variant="rage">
              <Plus className="w-4 h-4" /> Create New Plan
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {plans?.map((plan) => (
              <Card key={plan.id} className="flex flex-col justify-between border-zinc-800 bg-[#0f0f15] hover:border-red-600/50 transition-all">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="rage">{plan.duration_type}</Badge>
                    <span className="text-xs text-zinc-400">{plan.duration_days} Days</span>
                  </div>
                  <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                  <div className="mt-2 text-2xl font-black text-slate-900 dark:text-white font-mono">
                    ₹{plan.price.toLocaleString('en-IN')}
                    <span className="text-xs text-zinc-400 font-normal"> / cycle</span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-2">{plan.description}</p>
                  
                  <div className="mt-4 space-y-1.5 border-t border-zinc-800 pt-3">
                    {plan.features?.map((feat, fidx) => (
                      <div key={fidx} className="flex items-center gap-1.5 text-xs text-zinc-300">
                        <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 4. BRANCHES TAB */}
      {currentTab === 'admin-branches' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Gym Branch Locations</h2>
              <p className="text-xs text-zinc-400">Manage multi-location facility records and contact details</p>
            </div>
            <Button onClick={() => setIsBranchModalOpen(true)} variant="rage">
              <Plus className="w-4 h-4" /> Add Branch Location
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {branches?.map((branch) => (
              <Card key={branch.id} className="border-zinc-800">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-red-950/40 border border-red-800/40 text-red-400">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-base">{branch.name}</h3>
                      <span className="text-xs text-zinc-500 font-mono font-bold">{branch.code}</span>
                    </div>
                  </div>
                  <Badge variant="success">Active Branch</Badge>
                </div>
                <div className="mt-4 space-y-1 text-xs text-zinc-400 border-t border-zinc-800/80 pt-3">
                  <p>📍 {branch.address}, {branch.city}</p>
                  <p>📞 {branch.phone}</p>
                  {branch.email && <p>✉️ {branch.email}</p>}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 5. GLOBAL ATTENDANCE TAB */}
      {currentTab === 'admin-attendance' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Facility Attendance Records</h2>
            <p className="text-xs text-zinc-400">Live feed of gym floor access and member check-in history</p>
          </div>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase tracking-wider border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Member</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Check-In</th>
                  <th className="px-4 py-3">Check-Out</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Logged By</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {attendances?.map((att) => (
                  <tr key={att.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-bold text-white">{att.member_name}</td>
                    <td className="px-4 py-3 text-zinc-300 font-mono">{att.date}</td>
                    <td className="px-4 py-3 text-emerald-400 font-mono font-semibold">{att.check_in_time}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{att.check_out_time || 'In Gym'}</td>
                    <td className="px-4 py-3"><Badge variant="success">{att.status}</Badge></td>
                    <td className="px-4 py-3 text-zinc-400">{att.logged_by_name || 'Front Desk'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 6. PAYMENTS TAB */}
      {currentTab === 'admin-payments' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Revenue & Invoicing Ledger</h2>
            <p className="text-xs text-zinc-400">Complete transaction history, receipts, and payment methods</p>
          </div>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Invoice #</th>
                  <th className="px-4 py-3">Member</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Method</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {payments?.map((pay) => (
                  <tr key={pay.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-mono font-bold text-red-400">{pay.invoice_number}</td>
                    <td className="px-4 py-3 font-bold text-white">{pay.member_name}</td>
                    <td className="px-4 py-3 font-bold text-zinc-100 font-mono">₹{pay.amount.toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3 uppercase text-zinc-400">{pay.payment_method}</td>
                    <td className="px-4 py-3 capitalize text-zinc-300">{pay.payment_type}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{new Date(pay.transaction_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3"><Badge variant="success">{pay.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 7. CMS & SYSTEM CONFIGURATION TAB */}
      {currentTab === 'admin-settings' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <LayoutTemplate className="w-6 h-6 text-red-500" />
                Frontend CMS & Home Page Customizer
              </h2>
              <p className="text-xs text-zinc-400 mt-1">
                Customize your gym's brand identity, live landing page content, theme accent, hero messaging, and public metrics
              </p>
            </div>
            {savedSuccess && (
              <div className="px-4 py-2 bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs rounded-xl font-bold flex items-center gap-2 animate-in fade-in">
                <CheckCircle className="w-4 h-4" /> Live Website Updated Successfully!
              </div>
            )}
          </div>

          <form onSubmit={handleSaveSettings} className="space-y-6">
            {/* Brand & Theme Accent */}
            <Card className="border-zinc-800 p-6 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
                <Palette className="w-4 h-4 text-red-400" />
                <h3 className="font-bold text-white text-sm">Theme Accent & Brand Identity</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Gym Name</label>
                  <Input
                    value={settingsForm.gym_name}
                    onChange={(e) => setSettingsForm({ ...settingsForm, gym_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Brand Tagline</label>
                  <Input
                    value={settingsForm.tagline}
                    onChange={(e) => setSettingsForm({ ...settingsForm, tagline: e.target.value })}
                  />
                </div>
                <div className="md:col-span-3">
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-2 flex items-center gap-1.5">
                    <Palette className="w-3.5 h-3.5 text-red-400" /> Choose Frontend Theme Color & Ambient Glow
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
                    {[
                      { id: 'crimson', label: 'Crimson Rage', color: '#ef4444', border: 'border-red-500' },
                      { id: 'cyan', label: 'Electric Cyan', color: '#06b6d4', border: 'border-cyan-500' },
                      { id: 'emerald', label: 'Cyber Emerald', color: '#10b981', border: 'border-emerald-500' },
                      { id: 'gold', label: 'Royal Gold', color: '#f59e0b', border: 'border-amber-500' },
                      { id: 'violet', label: 'Neon Violet', color: '#8b5cf6', border: 'border-purple-500' },
                      { id: 'orange', label: 'Inferno Orange', color: '#f97316', border: 'border-orange-500' },
                    ].map((thm) => {
                      const isSelected = settingsForm.theme_accent === thm.id;
                      return (
                        <button
                          key={thm.id}
                          type="button"
                          onClick={() => setSettingsForm({ ...settingsForm, theme_accent: thm.id })}
                          className={`flex items-center gap-2 p-2.5 rounded-xl border transition-all cursor-pointer ${
                            isSelected
                              ? `bg-[#181824] ${thm.border} shadow-lg scale-[1.02]`
                              : 'bg-[#0e0e14] border-zinc-800 hover:border-zinc-700'
                          }`}
                        >
                          <span
                            className="w-4 h-4 rounded-full shrink-0 shadow-sm"
                            style={{ backgroundColor: thm.color }}
                          />
                          <span className="text-xs font-bold text-white truncate">{thm.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Top Announcement Banner</label>
                <Input
                  value={settingsForm.announcement_bar}
                  onChange={(e) => setSettingsForm({ ...settingsForm, announcement_bar: e.target.value })}
                />
              </div>
            </Card>

            {/* Landing Page Hero CMS */}
            <Card className="border-zinc-800 p-6 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
                <Globe className="w-4 h-4 text-red-400" />
                <h3 className="font-bold text-white text-sm">Landing Page Hero & CTA Settings</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Hero Main Headline</label>
                  <Input
                    value={settingsForm.hero_headline}
                    onChange={(e) => setSettingsForm({ ...settingsForm, hero_headline: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Hero Glowing Badge Text</label>
                  <Input
                    value={settingsForm.hero_badge_text}
                    onChange={(e) => setSettingsForm({ ...settingsForm, hero_badge_text: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Hero Subtitle Paragraph</label>
                <textarea
                  className="w-full px-3.5 py-2.5 bg-[#0a0a0e] border border-zinc-800 rounded-lg text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all h-20"
                  value={settingsForm.hero_subtitle}
                  onChange={(e) => setSettingsForm({ ...settingsForm, hero_subtitle: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Primary CTA Button Text</label>
                  <Input
                    value={settingsForm.hero_cta_primary}
                    onChange={(e) => setSettingsForm({ ...settingsForm, hero_cta_primary: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Secondary CTA Button Text</label>
                  <Input
                    value={settingsForm.hero_cta_secondary}
                    onChange={(e) => setSettingsForm({ ...settingsForm, hero_cta_secondary: e.target.value })}
                  />
                </div>
              </div>
            </Card>

            {/* Public Statistics Counters */}
            <Card className="border-zinc-800 p-6 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
                <Sparkles className="w-4 h-4 text-red-400" />
                <h3 className="font-bold text-white text-sm">Home Page Highlight Metric Counters</h3>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Access Hours</label>
                  <Input
                    value={settingsForm.stat_access_hours}
                    onChange={(e) => setSettingsForm({ ...settingsForm, stat_access_hours: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Equipment Quality</label>
                  <Input
                    value={settingsForm.stat_equipment_text}
                    onChange={(e) => setSettingsForm({ ...settingsForm, stat_equipment_text: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Trainers Count</label>
                  <Input
                    value={settingsForm.stat_trainers_count}
                    onChange={(e) => setSettingsForm({ ...settingsForm, stat_trainers_count: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Transformations</label>
                  <Input
                    value={settingsForm.stat_members_count}
                    onChange={(e) => setSettingsForm({ ...settingsForm, stat_members_count: e.target.value })}
                  />
                </div>
              </div>
            </Card>

            {/* General Contact & Currency Parameters */}
            <Card className="border-zinc-800 p-6 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
                <Building2 className="w-4 h-4 text-red-400" />
                <h3 className="font-bold text-white text-sm">Operating & Contact Information</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Contact Email</label>
                  <Input
                    value={settingsForm.contact_email}
                    onChange={(e) => setSettingsForm({ ...settingsForm, contact_email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Contact Phone</label>
                  <Input
                    value={settingsForm.contact_phone}
                    onChange={(e) => setSettingsForm({ ...settingsForm, contact_phone: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Physical Address</label>
                  <Input
                    value={settingsForm.address}
                    onChange={(e) => setSettingsForm({ ...settingsForm, address: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Currency Symbol</label>
                  <Input
                    value={settingsForm.currency_symbol}
                    onChange={(e) => setSettingsForm({ ...settingsForm, currency_symbol: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Tax (%)</label>
                  <Input
                    type="number"
                    value={settingsForm.tax_percentage}
                    onChange={(e) => setSettingsForm({ ...settingsForm, tax_percentage: Number(e.target.value) })}
                  />
                </div>
              </div>
            </Card>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button
                type="submit"
                variant="rage"
                size="lg"
                isLoading={updateSettingsMutation.isPending}
                className="px-8 cursor-pointer"
              >
                Save & Publish Changes Live
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* 8. LEADS & ENQUIRIES MANAGER TAB */}
      {currentTab === 'admin-enquiries' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <Users className="w-6 h-6 text-amber-400" />
                Leads & Assessment Enquiries
              </h2>
              <p className="text-xs text-zinc-400">
                Track prospective gym members, follow up via 1-click WhatsApp, and monitor lead conversion
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchEnquiries()}
              className="text-xs uppercase font-bold"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1" /> Refresh Leads
            </Button>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-[#111117] border border-zinc-800">
              <span className="text-xs text-zinc-400 uppercase font-bold">Total Enquiries</span>
              <div className="text-2xl font-black text-white mt-1 font-mono">{enquiries?.length || 0}</div>
            </div>
            <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40">
              <span className="text-xs text-amber-400 uppercase font-bold">New Uncontacted</span>
              <div className="text-2xl font-black text-amber-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'new').length || 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-800/40">
              <span className="text-xs text-blue-400 uppercase font-bold">In Discussion</span>
              <div className="text-2xl font-black text-blue-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'contacted').length || 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
              <span className="text-xs text-emerald-400 uppercase font-bold">Converted Members</span>
              <div className="text-2xl font-black text-emerald-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'converted').length || 0}
              </div>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input
                placeholder="Search by lead name, phone number, goal..."
                value={enquirySearch}
                onChange={(e) => setEnquirySearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select
              value={enquiryFilter}
              onChange={(e) => setEnquiryFilter(e.target.value)}
              className="sm:w-44"
            >
              <option value="all">All Statuses</option>
              <option value="new">New Only</option>
              <option value="contacted">Contacted</option>
              <option value="converted">Converted</option>
              <option value="closed">Closed</option>
            </Select>
          </div>

          {/* Enquiries Table */}
          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Lead Name</th>
                  <th className="px-4 py-3">Phone / WhatsApp</th>
                  <th className="px-4 py-3">Preferred Branch</th>
                  <th className="px-4 py-3">Fitness Goal</th>
                  <th className="px-4 py-3">Received Date</th>
                  <th className="px-4 py-3">Status Pipeline</th>
                  <th className="px-4 py-3">Direct Contact</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {filteredEnquiries?.map((enq) => {
                  const cleanPhone = enq.phone.replace(/[^0-9]/g, '');
                  const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(`Hi ${enq.name}, greetings from SETFIT Gym! We received your enquiry for ${enq.fitness_goal.replace(/_/g, ' ')}. How can we assist you today?`)}`;

                  return (
                    <tr key={enq.id} className="hover:bg-zinc-800/30 transition-colors">
                      <td className="px-4 py-3">
                        <span className="font-bold text-white text-sm block">{enq.name}</span>
                        <span className="text-zinc-500 text-[11px]">{enq.email || 'No email provided'}</span>
                        {enq.notes && <p className="text-zinc-400 text-[10px] mt-0.5 italic">"{enq.notes}"</p>}
                      </td>
                      <td className="px-4 py-3 font-mono text-zinc-200">{enq.phone}</td>
                      <td className="px-4 py-3 text-zinc-300">{enq.preferred_branch_name || 'Any Location'}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className="capitalize text-[10px]">
                          {enq.fitness_goal.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-zinc-400 font-mono">
                        {new Date(enq.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <select
                          value={enq.status}
                          onChange={(e) => handleUpdateEnquiryStatus(enq.id, e.target.value)}
                          className="px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-700 text-xs text-white font-bold cursor-pointer focus:border-red-500 outline-none"
                        >
                          <option value="new">🆕 New</option>
                          <option value="contacted">📞 Contacted</option>
                          <option value="converted">✅ Converted</option>
                          <option value="closed">❌ Closed</option>
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        <a
                          href={waUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 border border-emerald-500/30 font-bold text-xs transition-colors"
                        >
                          <MessageSquare className="w-3.5 h-3.5" />
                          WhatsApp
                        </a>
                      </td>
                    </tr>
                  );
                })}
                {(!filteredEnquiries || filteredEnquiries.length === 0) && (
                  <tr>
                    <td colSpan={7} className="text-center py-10 text-zinc-500">
                      No enquiries match your search or filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 9. PENDING UTR APPROVALS QUEUE TAB */}
      {currentTab === 'admin-verifications' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
                Pending UTR Verification Queue
              </h2>
              <p className="text-xs text-zinc-400">
                Review UPI transaction reference numbers submitted by registered members to activate subscriptions
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchPending()}
              className="text-xs uppercase font-bold"
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1" /> Refresh Queue
            </Button>
          </div>

          {pendingVerifications && pendingVerifications.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {pendingVerifications.map((item) => (
                <Card key={item.id} className="border-zinc-800 bg-[#0f0f15] p-5 flex flex-col justify-between shadow-lg">
                  <div>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <Badge variant="warning">Pending Approval</Badge>
                        <h3 className="font-bold text-white text-base mt-2">{item.member_name}</h3>
                        <p className="text-xs text-zinc-400">{item.member_email}</p>
                        <p className="text-xs font-mono text-zinc-400">{item.member_phone}</p>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-black text-emerald-400 font-mono">
                          ₹{item.amount.toLocaleString('en-IN')}
                        </span>
                        <p className="text-[11px] text-zinc-400 uppercase font-mono">{item.plan_name}</p>
                      </div>
                    </div>

                    <div className="my-4 p-3 rounded-xl bg-zinc-900/80 border border-zinc-800 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-400">12-Digit UTR No:</span>
                        <span className="font-mono font-bold text-amber-400 text-sm tracking-wider">
                          {item.utr_number}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-400">Target VPA:</span>
                        <span className="font-mono text-zinc-300">{item.upi_vpa || 'setfit@upi'}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-400">Submitted On:</span>
                        <span className="font-mono text-zinc-400">
                          {new Date(item.transaction_date).toLocaleString()}
                        </span>
                      </div>
                      {item.notes && (
                        <div className="text-xs text-zinc-400 pt-1 border-t border-zinc-800 italic">
                          "{item.notes}"
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-2 border-t border-zinc-800">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setRejectingPaymentId(item.id);
                        setRejectionReason('');
                      }}
                      className="text-xs uppercase font-bold text-red-400 hover:bg-red-950/50 hover:text-red-300"
                    >
                      <XCircle className="w-3.5 h-3.5 mr-1" /> Reject
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleVerifyUTR(item.id, item.member_name)}
                      isLoading={verifyPaymentMutation.isPending}
                      className="text-xs uppercase font-black bg-emerald-600 hover:bg-emerald-500 text-white"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Verify & Activate
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center border-zinc-800 bg-[#0c0c12]">
              <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
              <h3 className="text-lg font-black text-white uppercase">Queue is All Clear</h3>
              <p className="text-xs text-zinc-400 max-w-md mx-auto mt-1">
                There are currently no pending UTR payment submissions awaiting verification.
              </p>
            </Card>
          )}
        </div>
      )}

      {/* MODAL: REJECT UTR SUBMISSION */}
      <Modal
        isOpen={rejectingPaymentId !== null}
        onClose={() => setRejectingPaymentId(null)}
        title="Reject UTR Payment Verification"
        description="Specify a reason for rejecting this transaction reference"
      >
        <form onSubmit={handleRejectUTR} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">
              Rejection Reason *
            </label>
            <Input
              required
              placeholder="e.g. UTR reference not found in bank statement / incorrect amount"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setRejectingPaymentId(null)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={rejectPaymentMutation.isPending}
              className="bg-red-600 hover:bg-red-500 text-white font-bold"
            >
              Confirm Rejection
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: CREATE USER */}
      <Modal
        isOpen={isUserModalOpen}
        onClose={() => setIsUserModalOpen(false)}
        title="Add New Staff / Member"
        description="Create user credentials and assign access permissions"
      >
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">First Name</label>
              <Input
                required
                value={newUser.first_name}
                onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Last Name</label>
              <Input
                value={newUser.last_name}
                onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Email Address</label>
            <Input
              type="email"
              required
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Phone Number</label>
              <Input
                value={newUser.phone}
                onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Role Assignment</label>
              <Select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              >
                <option value="member">Member</option>
                <option value="trainer">Trainer</option>
                <option value="receptionist">Receptionist</option>
                <option value="admin">Admin</option>
              </Select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Temporary Password</label>
            <Input
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsUserModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={createUserMutation.isPending}>
              Create User Account
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: CREATE PLAN */}
      <Modal
        isOpen={isPlanModalOpen}
        onClose={() => setIsPlanModalOpen(false)}
        title="Create Membership Package"
        description="Define pricing tier, validity days and features"
      >
        <form onSubmit={handleCreatePlan} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Package Name</label>
            <Input
              required
              placeholder="e.g. Rage Platinum 6-Month"
              value={newPlan.name}
              onChange={(e) => setNewPlan({ ...newPlan, name: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Duration Type</label>
              <Select
                value={newPlan.duration_type}
                onChange={(e) => setNewPlan({ ...newPlan, duration_type: e.target.value })}
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="half_yearly">Half-Yearly</option>
                <option value="yearly">Yearly</option>
              </Select>
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Duration (Days)</label>
              <Input
                type="number"
                value={newPlan.duration_days}
                onChange={(e) => setNewPlan({ ...newPlan, duration_days: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Price (₹)</label>
              <Input
                type="number"
                value={newPlan.price}
                onChange={(e) => setNewPlan({ ...newPlan, price: Number(e.target.value) })}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Description</label>
            <Input
              placeholder="Brief summary of this tier"
              value={newPlan.description}
              onChange={(e) => setNewPlan({ ...newPlan, description: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Features (Comma Separated)</label>
            <Input
              placeholder="Sauna Access, Towel Service, 2 Guest Passes"
              value={newPlan.featuresStr}
              onChange={(e) => setNewPlan({ ...newPlan, featuresStr: e.target.value })}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsPlanModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={createPlanMutation.isPending}>
              Save Package
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: CREATE BRANCH */}
      <Modal
        isOpen={isBranchModalOpen}
        onClose={() => setIsBranchModalOpen(false)}
        title="Add Gym Branch"
        description="Register a new gym branch facility"
      >
        <form onSubmit={handleCreateBranch} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Branch Name</label>
              <Input
                required
                placeholder="Downtown Titanium HQ"
                value={newBranch.name}
                onChange={(e) => setNewBranch({ ...newBranch, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Branch Code (Unique)</label>
              <Input
                required
                placeholder="HQ-DT"
                value={newBranch.code}
                onChange={(e) => setNewBranch({ ...newBranch, code: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Address</label>
            <Input
              required
              placeholder="777 Titan Way"
              value={newBranch.address}
              onChange={(e) => setNewBranch({ ...newBranch, address: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">City</label>
              <Input
                required
                placeholder="Metropolis"
                value={newBranch.city}
                onChange={(e) => setNewBranch({ ...newBranch, city: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Contact Phone</label>
              <Input
                required
                placeholder="+1 (800) 555-7771"
                value={newBranch.phone}
                onChange={(e) => setNewBranch({ ...newBranch, phone: e.target.value })}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsBranchModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={createBranchMutation.isPending}>
              Register Branch
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
