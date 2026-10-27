import React, { useState } from 'react';
import {
  useReceptionistAnalyticsQuery, useSubscriptionsQuery, usePlansQuery,
  useOnboardMemberMutation, useRenewSubscriptionMutation,
  useAttendancesQuery, useCheckInMutation, useCheckOutMutation,
  useUsersQuery, usePaymentsQuery, usePendingVerificationsQuery,
  useVerifyPaymentMutation, useRejectPaymentMutation,
  useEnquiriesQuery, useUpdateEnquiryStatusMutation
} from '../../api/queries';
import {
  UserPlus, CalendarCheck, CreditCard, Search, CheckCircle,
  AlertTriangle, RefreshCw, UserCheck, MessageSquare,
  XCircle, CheckCircle2, ShieldCheck, Users
} from 'lucide-react';
import {
  Card, StatCard,
  Button, Badge, Modal, Input, Select
} from '../../components/ui';

interface ReceptionistPortalProps {
  currentTab: string;
}

export const ReceptionistPortal: React.FC<ReceptionistPortalProps> = ({ currentTab }) => {
  // Queries
  const { data: stats } = useReceptionistAnalyticsQuery();
  const { data: plans } = usePlansQuery();
  const { data: members } = useUsersQuery({ role: 'member' });
  const { data: subscriptions } = useSubscriptionsQuery();
  const { data: attendances } = useAttendancesQuery();
  const { data: payments } = usePaymentsQuery();
  const { data: pendingVerifications, refetch: refetchPending } = usePendingVerificationsQuery();
  const { data: enquiries, refetch: refetchEnquiries } = useEnquiriesQuery();

  // Mutations
  const onboardMutation = useOnboardMemberMutation();
  const renewMutation = useRenewSubscriptionMutation();
  const checkInMutation = useCheckInMutation();
  const checkOutMutation = useCheckOutMutation();
  const verifyPaymentMutation = useVerifyPaymentMutation();
  const rejectPaymentMutation = useRejectPaymentMutation();
  const updateEnquiryStatusMutation = useUpdateEnquiryStatusMutation();

  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubForRenew, setSelectedSubForRenew] = useState<any | null>(null);
  const [isRenewModalOpen, setIsRenewModalOpen] = useState(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);
  const [rejectingPaymentId, setRejectingPaymentId] = useState<number | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [enquiryFilter, setEnquiryFilter] = useState('all');
  const [enquirySearch, setEnquirySearch] = useState('');

  // Onboarding Form
  const [onboardData, setOnboardData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    plan_id: plans?.[0]?.id || 1,
    payment_method: 'card',
    amount_paid: '',
    notes: 'Onboarded at front desk',
  });

  // Renewal Form
  const [renewPlanId, setRenewPlanId] = useState<number>(1);
  const [renewPaymentMethod, setRenewPaymentMethod] = useState('card');

  const handleOnboardSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessNotice(null);
    try {
      const selectedPlan = plans?.find((p) => p.id === Number(onboardData.plan_id));
      const amount = onboardData.amount_paid ? Number(onboardData.amount_paid) : (selectedPlan?.price || 49);
      
      const res: any = await onboardMutation.mutateAsync({
        first_name: onboardData.first_name,
        last_name: onboardData.last_name,
        email: onboardData.email,
        phone: onboardData.phone,
        plan_id: Number(onboardData.plan_id),
        payment_method: onboardData.payment_method,
        amount_paid: amount,
        payment_notes: onboardData.notes,
      });

      setSuccessNotice(`Member ${onboardData.first_name} onboarded! Invoice: ${res.invoice_number}`);
      setOnboardData({
        first_name: '', last_name: '', email: '', phone: '',
        plan_id: plans?.[0]?.id || 1, payment_method: 'card',
        amount_paid: '', notes: 'Onboarded at front desk',
      });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to onboard member');
    }
  };

  const handleFastCheckIn = async (memberId: number) => {
    try {
      await checkInMutation.mutateAsync({ member_id: memberId });
      setSuccessNotice(`Check-in recorded!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to check-in');
    }
  };

  const handleRenewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSubForRenew) return;
    try {
      await renewMutation.mutateAsync({
        id: selectedSubForRenew.id,
        data: {
          plan_id: Number(renewPlanId),
          payment_method: renewPaymentMethod,
          notes: 'Front-desk extension',
        },
      });
      setIsRenewModalOpen(false);
      setSelectedSubForRenew(null);
      setSuccessNotice(`Membership renewed successfully!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to renew subscription');
    }
  };

  const handleVerifyUTR = async (paymentId: number, memberName: string) => {
    try {
      await verifyPaymentMutation.mutateAsync({ paymentId });
      setSuccessNotice(`Verified payment & activated membership for ${memberName}!`);
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
      setSuccessNotice('Payment verification rejected. Member notified to submit valid reference.');
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

  // Filter subscriptions for renewals
  const expiringSubscriptions = subscriptions?.filter((s) => {
    return s.days_left <= 7 || s.status === 'expired';
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
      {successNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-700 text-emerald-300 text-sm flex items-center justify-between animate-in fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span>{successNotice}</span>
          </div>
          <button onClick={() => setSuccessNotice(null)} className="text-emerald-400 hover:text-white font-bold">✕</button>
        </div>
      )}

      {/* 1. FRONT DESK OVERVIEW */}
      {(currentTab === 'rec-dashboard' || !currentTab) && (
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
              <span>Front-Desk Command Terminal</span>
              <Badge variant="purple">Receptionist</Badge>
            </h1>
            <p className="text-xs text-zinc-400 mt-1">Daily member check-ins, walk-in onboarding, and membership renewals</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Today's Check-ins"
              value={stats?.today_checkins || 0}
              subtitle="Members active in facility"
              icon={CalendarCheck}
              accent="rage"
            />
            <StatCard
              title="Active Members"
              value={stats?.total_members || 0}
              subtitle={`${stats?.active_members || 0} currently paid`}
              icon={UserCheck}
              accent="emerald"
            />
            <StatCard
              title="Expiring in 7 Days"
              value={stats?.expiring_soon_7days || 0}
              subtitle="Urgent renewal follow-ups"
              icon={AlertTriangle}
              accent="amber"
            />
            <StatCard
              title="Today's Intake"
              value={`₹${(stats?.today_revenue || 0).toLocaleString('en-IN')}`}
              subtitle="Payments collected today"
              icon={CreditCard}
              accent="blue"
            />
          </div>

          {/* Quick Actions Bar */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-red-900/30 bg-[#121218] p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-red-950 text-red-400"><UserPlus className="w-5 h-5" /></div>
                <div>
                  <h3 className="font-bold text-white text-sm">Walk-in Registration</h3>
                  <p className="text-xs text-zinc-400">Onboard new gym member</p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 mb-4">Complete member account creation, package selection, and payment receipt.</p>
            </Card>

            <Card className="border-emerald-900/30 bg-[#121218] p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-emerald-950 text-emerald-400"><CalendarCheck className="w-5 h-5" /></div>
                <div>
                  <h3 className="font-bold text-white text-sm">Express Check-in</h3>
                  <p className="text-xs text-zinc-400">Log member access</p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 mb-4">Fast 1-click check-in for registered members entering the gym floor.</p>
            </Card>

            <Card className="border-amber-900/30 bg-[#121218] p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-lg bg-amber-950 text-amber-400"><RefreshCw className="w-5 h-5" /></div>
                <div>
                  <h3 className="font-bold text-white text-sm">Renewals Queue</h3>
                  <p className="text-xs text-zinc-400">Extend subscriptions</p>
                </div>
              </div>
              <p className="text-xs text-zinc-400 mb-4">Process dues and renew memberships expiring within 7 days.</p>
            </Card>
          </div>
        </div>
      )}

      {/* 2. MEMBER ONBOARDING TAB */}
      {currentTab === 'rec-onboarding' && (
        <div className="max-w-2xl space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Onboard New Member</h2>
            <p className="text-xs text-zinc-400">Create member account, assign membership package, and collect initial dues</p>
          </div>

          <Card className="border-zinc-800 p-6">
            <form onSubmit={handleOnboardSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">First Name *</label>
                  <Input
                    required
                    placeholder="John"
                    value={onboardData.first_name}
                    onChange={(e) => setOnboardData({ ...onboardData, first_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Last Name</label>
                  <Input
                    placeholder="Doe"
                    value={onboardData.last_name}
                    onChange={(e) => setOnboardData({ ...onboardData, last_name: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Email Address *</label>
                  <Input
                    type="email"
                    required
                    placeholder="john.doe@example.com"
                    value={onboardData.email}
                    onChange={(e) => setOnboardData({ ...onboardData, email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Phone Number *</label>
                  <Input
                    required
                    placeholder="+1 (555) 000-0000"
                    value={onboardData.phone}
                    onChange={(e) => setOnboardData({ ...onboardData, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-zinc-800">
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Membership Plan</label>
                  <Select
                    value={onboardData.plan_id}
                    onChange={(e) => setOnboardData({ ...onboardData, plan_id: Number(e.target.value) })}
                  >
                    {plans?.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} — ${p.price} ({p.duration_days} days)
                      </option>
                    ))}
                  </Select>
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Payment Method</label>
                  <Select
                    value={onboardData.payment_method}
                    onChange={(e) => setOnboardData({ ...onboardData, payment_method: e.target.value })}
                  >
                    <option value="card">Credit/Debit Card</option>
                    <option value="cash">Cash</option>
                    <option value="upi">UPI / Online</option>
                    <option value="bank_transfer">Bank Wire</option>
                  </Select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase text-zinc-300 mb-1">Registration Notes</label>
                <Input
                  value={onboardData.notes}
                  onChange={(e) => setOnboardData({ ...onboardData, notes: e.target.value })}
                />
              </div>

              <Button
                type="submit"
                variant="rage"
                size="lg"
                className="w-full mt-3"
                isLoading={onboardMutation.isPending}
              >
                Complete Registration & Process Payment
              </Button>
            </form>
          </Card>
        </div>
      )}

      {/* 3. FAST ATTENDANCE CHECK-IN TAB */}
      {currentTab === 'rec-attendance' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Express Attendance Check-In</h2>
              <p className="text-xs text-zinc-400">Search members and record immediate gym entry</p>
            </div>
          </div>

          <div className="bg-[#111116] p-4 rounded-xl border border-zinc-800 space-y-3">
            <div className="relative">
              <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3.5" />
              <Input
                placeholder="Search member name, email, or phone..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 py-3"
              />
            </div>

            {/* Quick Member Search Results */}
            {searchQuery.length > 0 && (
              <div className="divide-y divide-zinc-800/80 max-h-60 overflow-y-auto bg-[#0a0a0f] rounded-lg border border-zinc-800">
                {members
                  ?.filter((m) =>
                    `${m.first_name} ${m.last_name} ${m.email} ${m.phone}`
                      .toLowerCase()
                      .includes(searchQuery.toLowerCase())
                  )
                  .map((m) => (
                    <div key={m.id} className="p-3 flex items-center justify-between hover:bg-zinc-800/40">
                      <div>
                        <span className="font-bold text-white text-sm">{m.first_name} {m.last_name}</span>
                        <div className="text-xs text-zinc-400">{m.email} • {m.phone}</div>
                      </div>
                      <Button
                        size="sm"
                        variant="rage"
                        onClick={() => handleFastCheckIn(m.id)}
                        isLoading={checkInMutation.isPending}
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Mark Present
                      </Button>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Today's Logged Attendance */}
          <Card className="overflow-x-auto p-0 border-zinc-800">
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
              <h3 className="font-bold text-white text-sm">Today's Check-in Log</h3>
              <Badge variant="success">Live Gym Floor</Badge>
            </div>
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Member Name</th>
                  <th className="px-4 py-3">Check-In Time</th>
                  <th className="px-4 py-3">Check-Out</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {attendances?.map((att) => (
                  <tr key={att.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-bold text-white">{att.member_name}</td>
                    <td className="px-4 py-3 text-emerald-400 font-mono font-bold">{att.check_in_time}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{att.check_out_time || 'In Session'}</td>
                    <td className="px-4 py-3"><Badge variant="success">{att.status}</Badge></td>
                    <td className="px-4 py-3 text-right">
                      {!att.check_out_time && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => checkOutMutation.mutate({ attendance_id: att.id })}
                        >
                          Check Out
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

      {/* 4. RENEWALS & EXPIRY TRACKER */}
      {currentTab === 'rec-renewals' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Expiring Subscriptions & Renewals</h2>
            <p className="text-xs text-zinc-400">Members due for renewal within 7 days or expired subscriptions</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {expiringSubscriptions?.map((sub) => {
              const isExpired = sub.status === 'expired' || sub.days_left === 0;
              return (
                <Card
                  key={sub.id}
                  className={`border ${
                    isExpired ? 'border-rose-900/50 bg-rose-950/10' : 'border-amber-900/50 bg-amber-950/10'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant={isExpired ? 'danger' : 'warning'}>
                      {isExpired ? 'Expired' : `${sub.days_left} Days Left`}
                    </Badge>
                    <span className="text-xs font-mono text-zinc-400">Ends: {sub.end_date}</span>
                  </div>

                  <h3 className="font-bold text-white text-base">{sub.member_name}</h3>
                  <p className="text-xs text-zinc-400 font-mono">{sub.member_email}</p>
                  <p className="text-xs text-zinc-400 font-mono">{sub.member_phone}</p>

                  <div className="mt-3 pt-3 border-t border-zinc-800/80 flex items-center justify-between">
                    <div>
                      <span className="text-xs text-zinc-500">Plan:</span>
                      <p className="text-xs font-bold text-zinc-200">{sub.plan_name}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="rage"
                      onClick={() => {
                        setSelectedSubForRenew(sub);
                        setRenewPlanId(sub.plan_id);
                        setIsRenewModalOpen(true);
                      }}
                    >
                      Renew Now
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. PAYMENTS TAB */}
      {currentTab === 'rec-payments' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Front-Desk Receipts & Invoices</h2>
            <p className="text-xs text-zinc-400">Payment logs generated at front-desk</p>
          </div>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Invoice Number</th>
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
                    <td className="px-4 py-3 font-bold text-white font-mono">₹{pay.amount.toLocaleString('en-IN')}</td>
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

      {/* 6. LEADS & ENQUIRIES TAB */}
      {currentTab === 'rec-enquiries' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <Users className="w-6 h-6 text-amber-400" />
                Prospect Leads & Enquiries
              </h2>
              <p className="text-xs text-zinc-400">
                Front-desk lead follow-up, 1-click WhatsApp messaging, and trial booking
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
              <span className="text-xs text-zinc-400 uppercase font-bold">Total Leads</span>
              <div className="text-2xl font-black text-white mt-1 font-mono">{enquiries?.length || 0}</div>
            </div>
            <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/40">
              <span className="text-xs text-amber-400 uppercase font-bold">New Uncontacted</span>
              <div className="text-2xl font-black text-amber-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'new').length || 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-blue-950/30 border border-blue-800/40">
              <span className="text-xs text-blue-400 uppercase font-bold">Contacted</span>
              <div className="text-2xl font-black text-blue-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'contacted').length || 0}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
              <span className="text-xs text-emerald-400 uppercase font-bold">Joined Gym</span>
              <div className="text-2xl font-black text-emerald-400 mt-1 font-mono">
                {enquiries?.filter((e) => e.status === 'converted').length || 0}
              </div>
            </div>
          </div>

          {/* Search & Filter */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input
                placeholder="Search lead by name, mobile, goal..."
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

          {/* Table */}
          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Lead Name</th>
                  <th className="px-4 py-3">Mobile Phone</th>
                  <th className="px-4 py-3">Branch</th>
                  <th className="px-4 py-3">Fitness Goal</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Status Pipeline</th>
                  <th className="px-4 py-3">WhatsApp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {filteredEnquiries?.map((enq) => {
                  const cleanPhone = enq.phone.replace(/[^0-9]/g, '');
                  const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(`Hi ${enq.name}, this is Front Desk from SETFIT Gym. Regarding your interest in ${enq.fitness_goal.replace(/_/g, ' ')}, when would you like to visit for your trial?`)}`;

                  return (
                    <tr key={enq.id} className="hover:bg-zinc-800/30">
                      <td className="px-4 py-3">
                        <span className="font-bold text-white text-sm block">{enq.name}</span>
                        <span className="text-zinc-500 text-[11px]">{enq.email || '—'}</span>
                        {enq.notes && <p className="text-zinc-400 text-[10px] mt-0.5 italic">"{enq.notes}"</p>}
                      </td>
                      <td className="px-4 py-3 font-mono text-zinc-200">{enq.phone}</td>
                      <td className="px-4 py-3 text-zinc-300">{enq.preferred_branch_name || 'Any Location'}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className="capitalize text-[10px]">
                          {enq.fitness_goal.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-zinc-400 font-mono">{new Date(enq.created_at).toLocaleDateString()}</td>
                      <td className="px-4 py-3">
                        <select
                          value={enq.status}
                          onChange={(e) => handleUpdateEnquiryStatus(enq.id, e.target.value)}
                          className="px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-700 text-xs text-white font-bold cursor-pointer outline-none focus:border-purple-500"
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
                          Chat
                        </a>
                      </td>
                    </tr>
                  );
                })}
                {(!filteredEnquiries || filteredEnquiries.length === 0) && (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-zinc-500">
                      No leads found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 7. PENDING UTR VERIFICATIONS TAB */}
      {currentTab === 'rec-verifications' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
                Member UTR Payment Approvals
              </h2>
              <p className="text-xs text-zinc-400">
                Confirm UPI reference IDs and unlock active passes for new or renewing athletes
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
                        <Badge variant="warning">Needs Approval</Badge>
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
                        <span className="text-zinc-400">12-Digit UTR Ref:</span>
                        <span className="font-mono font-bold text-amber-400 text-sm tracking-wider">
                          {item.utr_number}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-400">VPA:</span>
                        <span className="font-mono text-zinc-300">{item.upi_vpa || 'setfit@upi'}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-zinc-400">Submitted:</span>
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
              <h3 className="text-lg font-black text-white uppercase">All Caught Up</h3>
              <p className="text-xs text-zinc-400 max-w-md mx-auto mt-1">
                No member UTR submissions pending review at front-desk right now.
              </p>
            </Card>
          )}
        </div>
      )}

      {/* MODAL: REJECT UTR SUBMISSION */}
      <Modal
        isOpen={rejectingPaymentId !== null}
        onClose={() => setRejectingPaymentId(null)}
        title="Reject Payment Reference"
        description="Provide a reason for rejecting this UTR verification"
      >
        <form onSubmit={handleRejectUTR} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">
              Reason for Rejection *
            </label>
            <Input
              required
              placeholder="e.g. Transaction reference not found in bank statement"
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

      {/* MODAL: RENEW MEMBERSHIP */}
      <Modal
        isOpen={isRenewModalOpen}
        onClose={() => setIsRenewModalOpen(false)}
        title="Renew Member Subscription"
        description={`Renewing plan for ${selectedSubForRenew?.member_name}`}
      >
        <form onSubmit={handleRenewSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Select Renewal Package</label>
            <Select
              value={renewPlanId}
              onChange={(e) => setRenewPlanId(Number(e.target.value))}
            >
              {plans?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} — ₹{p.price.toLocaleString('en-IN')} ({p.duration_days} days)
                </option>
              ))}
            </Select>
          </div>

          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Payment Method</label>
            <Select
              value={renewPaymentMethod}
              onChange={(e) => setRenewPaymentMethod(e.target.value)}
            >
              <option value="card">Credit/Debit Card</option>
              <option value="cash">Cash</option>
              <option value="upi">UPI / Online</option>
              <option value="bank_transfer">Bank Wire</option>
            </Select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsRenewModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={renewMutation.isPending}>
              Confirm Renewal & Process Payment
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
