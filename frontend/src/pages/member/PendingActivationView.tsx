import React, { useState } from 'react';
import {
  usePlansQuery, useGymSettingsQuery, useSubmitUTRMutation,
  useMyActiveSubscriptionQuery, usePaymentsQuery
} from '../../api/queries';
import {
  QrCode, Copy, CheckCircle2, Clock, AlertCircle,
  ExternalLink, Flame, Shield, ArrowRight
} from 'lucide-react';
import { Card, Button, Badge, Input } from '../../components/ui';

interface PendingActivationViewProps {
  onPassActivated?: () => void;
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

export const PendingActivationView: React.FC<PendingActivationViewProps> = () => {
  const { data: serverPlans } = usePlansQuery();
  const { data: settings } = useGymSettingsQuery();
  const { data: subscription } = useMyActiveSubscriptionQuery();
  const { data: payments } = usePaymentsQuery();
  const submitUTRMutation = useSubmitUTRMutation();

  const plans = serverPlans && serverPlans.length > 0 ? serverPlans : FALLBACK_PLANS;

  // Selected plan state
  const initialPlanId = subscription?.plan_id || plans[0]?.id || 1;
  const [selectedPlanId, setSelectedPlanId] = useState<number>(initialPlanId);
  const selectedPlan = plans.find((p) => p.id === selectedPlanId) || plans[0];

  // UTR submission state
  const [utrNumber, setUtrNumber] = useState('');
  const [notes, setNotes] = useState('');
  const [copied, setCopied] = useState(false);
  const [submittedSuccess, setSubmittedSuccess] = useState(false);

  const latestPayment = payments?.find((p) => p.subscription_id === subscription?.id) || payments?.[0];
  const isPendingVerification = latestPayment?.status === 'pending_verification' || subscription?.status === 'pending_verification';
  const isRejected = latestPayment?.status === 'rejected';

  const upiId = settings?.upi_id || 'setfit@upi';
  const gymName = settings?.gym_name || 'SETFIT GYM';
  const amount = selectedPlan.price;

  // Generate standard UPI Payment URL
  const upiUrl = `upi://pay?pa=${encodeURIComponent(upiId)}&pn=${encodeURIComponent(gymName)}&am=${amount}&cu=INR&tn=${encodeURIComponent(`SETFIT_${selectedPlan.name.replace(/\s+/g, '_')}`)}`;
  const qrCodeImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=260x260&data=${encodeURIComponent(upiUrl)}&margin=10`;

  const handleCopyUPI = () => {
    navigator.clipboard.writeText(upiId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSubmitUTR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!utrNumber.trim()) return;

    await submitUTRMutation.mutateAsync({
      plan_id: selectedPlan.id,
      utr_number: utrNumber.trim(),
      upi_vpa: upiId,
      notes: notes.trim(),
    });

    setSubmittedSuccess(true);
    setUtrNumber('');
  };

  const whatsappPhone = settings?.contact_phone?.replace(/[^0-9]/g, '') || '919876500001';
  const whatsappMessage = encodeURIComponent(
    `Hello ${gymName}, I have completed my UPI payment of ₹${amount.toLocaleString('en-IN')} for the ${selectedPlan.name} membership. My UTR Number is: ${latestPayment?.utr_number || utrNumber || 'Pending verification'}. Please verify and activate my athlete pass.`
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in">
      {/* Banner Notice */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-950/80 via-slate-900 to-[#0d0d12] border border-amber-800/40 p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Badge variant="warning">Step 2: Account Activation Pending</Badge>
              <span className="text-[11px] font-mono text-amber-400 font-bold flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> Instant UPI Verification
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Activate Your Training Pass
            </h1>
            <p className="text-xs text-slate-300 max-w-xl">
              Scan the dynamic UPI QR code below with any UPI App (GPay, PhonePe, Paytm), complete the payment in Indian Rupees (₹), and enter your 12-digit UTR transaction number for instant pass activation.
            </p>
          </div>

          <div className="flex items-center gap-3 bg-black/50 backdrop-blur-md px-5 py-3 rounded-2xl border border-amber-500/20 text-right">
            <div>
              <span className="text-[10px] uppercase font-bold text-amber-400">Total Payable</span>
              <div className="text-2xl font-black text-white font-mono">
                ₹{amount.toLocaleString('en-IN')}
              </div>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
              <Flame className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      {/* Rejection Alert if applicable */}
      {isRejected && (
        <div className="p-4 rounded-2xl bg-red-950/80 border border-red-800 text-red-200 text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <div>
              <strong className="text-white block font-bold">Previous UTR Verification Failed</strong>
              <span>Reason: {latestPayment?.rejection_reason || 'Bank reference not matching. Please check your 12-digit UTR and resubmit.'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: QR & Payment Info vs Plan Selection & UTR Form */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Dynamic UPI QR Code & Instructions */}
        <Card className="lg:col-span-5 border-slate-200 dark:border-white/10 p-6 flex flex-col justify-between space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-zinc-800 text-slate-800 dark:text-zinc-200 text-[11px] font-black uppercase tracking-wider">
              <QrCode className="w-3.5 h-3.5 text-emerald-500" /> Dynamic UPI QR Code
            </div>
            <h3 className="text-lg font-black text-slate-900 dark:text-white uppercase tracking-wide">
              Scan with Any UPI App
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              Compatible with Google Pay, PhonePe, Paytm, BHIM & Cred
            </p>
          </div>

          {/* QR Code Presentation Frame */}
          <div className="flex flex-col items-center justify-center p-4 rounded-2xl bg-white dark:bg-zinc-900 border-2 border-dashed border-slate-300 dark:border-zinc-700 shadow-inner">
            <img
              src={qrCodeImageUrl}
              alt="SETFIT UPI QR Code"
              className="w-52 h-52 rounded-xl shadow-md border border-slate-100 dark:border-zinc-800"
            />
            <div className="mt-3 text-center">
              <span className="text-xs font-mono font-black text-slate-900 dark:text-white">
                AMOUNT: ₹{amount.toLocaleString('en-IN')}
              </span>
              <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                Merchant: {gymName}
              </p>
            </div>
          </div>

          {/* Copyable UPI VPA info */}
          <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-white/10 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase text-slate-500 dark:text-zinc-400 block">
                Official UPI VPA ID
              </span>
              <span className="text-xs font-mono font-black text-slate-900 dark:text-white">
                {upiId}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyUPI}
              className="text-xs gap-1.5 cursor-pointer"
            >
              {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy UPI'}</span>
            </Button>
          </div>

          {/* WhatsApp Support Direct Button */}
          <a
            href={`https://wa.me/${whatsappPhone}?text=${whatsappMessage}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 p-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs uppercase tracking-wider transition-colors shadow-sm"
          >
            <span>💬 Fast-Track Approval on WhatsApp</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </Card>

        {/* Right Column: Plan Tier Switcher & UTR Submission Form */}
        <div className="lg:col-span-7 space-y-6">
          {/* Step A: Select / Confirm Plan Tier */}
          <Card className="border-slate-200 dark:border-white/10 p-6 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-white/10">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                  1
                </span>
                <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase">
                  Select / Change Pass Tier (₹ / INR)
                </h3>
              </div>
              <Badge variant="rage">{selectedPlan.duration_type}</Badge>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {plans.map((plan) => {
                const isSelected = selectedPlanId === plan.id;
                return (
                  <button
                    key={plan.id}
                    type="button"
                    onClick={() => setSelectedPlanId(plan.id)}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-slate-900 text-white dark:bg-white dark:text-black border-slate-900 dark:border-white shadow-md font-bold'
                        : 'bg-slate-50 dark:bg-zinc-900/60 border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300 hover:border-slate-400'
                    }`}
                  >
                    <div className="text-[10px] uppercase font-mono opacity-80">{plan.duration_type}</div>
                    <div className="text-xs font-black truncate mt-0.5">{plan.name.split(' ')[0]}</div>
                    <div className="text-sm font-black font-mono mt-1">₹{plan.price.toLocaleString('en-IN')}</div>
                  </button>
                );
              })}
            </div>
          </Card>

          {/* Step B: UTR Submission Form or Pending Verification Banner */}
          <Card className="border-slate-200 dark:border-white/10 p-6 space-y-5">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-white/10">
              <span className="w-5 h-5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-black text-[11px] font-black flex items-center justify-center">
                2
              </span>
              <h3 className="text-xs font-black text-slate-900 dark:text-white tracking-widest uppercase">
                Submit 12-Digit UTR Number
              </h3>
            </div>

            {/* Pending Verification Notice if already submitted */}
            {isPendingVerification && !submittedSuccess && (
              <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/50 border border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-200 space-y-2">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400 animate-spin" />
                  <strong className="text-xs font-bold uppercase tracking-wider">
                    UTR Verification in Progress
                  </strong>
                </div>
                <p className="text-xs">
                  Submitted UTR Reference: <strong className="font-mono text-slate-900 dark:text-white">{latestPayment?.utr_number || 'Under Review'}</strong>
                </p>
                <p className="text-[11px] text-amber-700 dark:text-amber-400">
                  Our front desk & accounting team are checking bank settlement records. Your dashboard will automatically unlock upon confirmation.
                </p>
              </div>
            )}

            {submittedSuccess && (
              <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200 flex items-center gap-2.5 text-xs">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <div>
                  <strong className="block font-bold">Payment Proof Submitted Successfully!</strong>
                  <span>Your UTR has been sent to the Admin Verification Queue. Status updates live.</span>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmitUTR} className="space-y-4" autoComplete="off">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5 flex items-center justify-between">
                  <span>12-Digit UTR / Transaction Reference ID *</span>
                  <span className="text-[10px] text-slate-400 lowercase font-normal">Found in your payment app receipt</span>
                </label>
                <Input
                  required
                  placeholder="e.g. 425689104523"
                  value={utrNumber}
                  onChange={(e) => setUtrNumber(e.target.value)}
                  className="font-mono tracking-widest text-sm"
                  autoComplete="off"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
                  Payment App / Bank Remarks (Optional)
                </label>
                <Input
                  placeholder="e.g. Paid via Google Pay / HDFC Bank"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  autoComplete="off"
                />
              </div>

              <div className="p-3.5 rounded-xl bg-slate-100 dark:bg-zinc-900 text-xs space-y-1 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-white/10">
                <div className="flex items-center justify-between text-slate-900 dark:text-white font-bold">
                  <span>Activation Policy</span>
                  <span className="text-emerald-600 dark:text-emerald-400 font-mono">100% Protected</span>
                </div>
                <p className="text-[11px]">
                  Pass validity starts from the moment your payment is verified by our desk. Zero lost days.
                </p>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={submitUTRMutation.isPending}
                className="w-full uppercase text-xs font-black tracking-wider py-4 cursor-pointer gap-2"
              >
                <span>Submit UTR for Verification</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </form>
          </Card>

          {/* Security badge */}
          <div className="flex items-center justify-center gap-2 text-xs text-slate-500 dark:text-zinc-500">
            <Shield className="w-4 h-4 text-emerald-500" />
            <span>256-Bit Encrypted Bank Reconciliation & Anti-Fraud Security</span>
          </div>
        </div>
      </div>
    </div>
  );
};
