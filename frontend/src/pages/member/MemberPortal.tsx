import React, { useState } from 'react';
import {
  useMemberAnalyticsQuery, useMyActiveSubscriptionQuery,
  useMyActiveWorkoutQuery, useMyActiveDietQuery,
  useAttendancesQuery, usePaymentsQuery
} from '../../api/queries';
import {
  Flame, Dumbbell, Utensils, CalendarCheck,
  Award, AlertTriangle, RefreshCw
} from 'lucide-react';
import {
  Card, CardHeader, CardTitle, CardContent, StatCard,
  Badge, Button
} from '../../components/ui';
import { PendingActivationView } from './PendingActivationView';

interface MemberPortalProps {
  currentTab: string;
}

export const MemberPortal: React.FC<MemberPortalProps> = ({ currentTab }) => {
  const { data: stats } = useMemberAnalyticsQuery();
  const { data: subscription, isLoading: isSubLoading } = useMyActiveSubscriptionQuery();
  const { data: workout } = useMyActiveWorkoutQuery();
  const { data: diet } = useMyActiveDietQuery();
  const { data: attendances } = useAttendancesQuery();
  const { data: payments } = usePaymentsQuery();

  const [showRenewModal, setShowRenewModal] = useState(false);

  // If the user does not have an active subscription or is pending verification
  const isPendingOrInactive = !isSubLoading && (!subscription || subscription.status === 'pending_verification' || subscription.status === 'expired' || subscription.status === 'cancelled');

  if (isPendingOrInactive || showRenewModal) {
    return (
      <div className="space-y-6">
        {showRenewModal && subscription?.status === 'active' && (
          <div className="flex justify-end">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRenewModal(false)}
              className="text-xs font-bold uppercase"
            >
              ← Back to Athlete Hub
            </Button>
          </div>
        )}
        <PendingActivationView onPassActivated={() => setShowRenewModal(false)} />
      </div>
    );
  }

  const isExpiringSoon = subscription?.status === 'active' && (subscription.days_left !== undefined && subscription.days_left <= 3);

  return (
    <div className="space-y-6">
      {/* Expiry Warning Banner (<= 3 days) */}
      {isExpiringSoon && (
        <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-amber-600 dark:text-amber-400">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <div>
              <p className="text-sm font-black uppercase">
                Membership Pass Renewal Reminder
              </p>
              <p className="text-xs opacity-90">
                Your pass expires in <strong>{subscription.days_left} days</strong> ({subscription.end_date}). Renew early to avoid check-in disruption.
              </p>
            </div>
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowRenewModal(true)}
            className="text-xs uppercase font-black shrink-0 bg-amber-500 text-black hover:bg-amber-400"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1" />
            Renew Pass (₹)
          </Button>
        </div>
      )}

      {/* 1. PERSONAL FITNESS HUB */}
      {(currentTab === 'member-dashboard' || !currentTab) && (
        <div className="space-y-6">
          {/* Welcome & Membership Banner */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-red-950/80 via-[#14141c] to-[#0a0a0f] border border-red-900/40 p-6 shadow-panel">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="rage">VIP Athlete Portal</Badge>
                  {subscription?.status === 'active' ? (
                    <Badge variant="success">Active Pass</Badge>
                  ) : (
                    <Badge variant="danger">Inactive</Badge>
                  )}
                </div>
                <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  Welcome to Your Training Command
                </h1>
                <p className="text-xs text-zinc-300 mt-1">
                  Plan: <strong className="text-red-400 font-bold">{subscription?.plan_name || 'Standard Tier'}</strong> • Valid Until: <strong className="text-zinc-200 font-mono">{subscription?.end_date || '—'}</strong>
                </p>
              </div>

              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRenewModal(true)}
                  className="text-xs uppercase font-bold"
                >
                  <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                  Renew / Upgrade Pass
                </Button>

                <div className="flex items-center gap-3 bg-black/40 backdrop-blur-md px-4 py-3 rounded-xl border border-zinc-800">
                  <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-zinc-400">Pass Validity</span>
                    <div className="text-2xl font-black text-red-500 font-mono">
                      {subscription?.days_left ?? 0} <span className="text-xs text-zinc-400 font-normal">days</span>
                    </div>
                  </div>
                  <div className="w-10 h-10 rounded-xl bg-red-600/20 border border-red-500/40 flex items-center justify-center text-red-500">
                    <Flame className="w-6 h-6" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* KPI Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Gym Visits This Month"
              value={stats?.total_checkins_this_month || 0}
              subtitle="Sessions logged"
              icon={CalendarCheck}
              accent="rage"
            />
            <StatCard
              title="Active Routine"
              value={workout ? 'Assigned' : 'Pending'}
              subtitle={workout?.title || 'Consult coach'}
              icon={Dumbbell}
              accent="emerald"
            />
            <StatCard
              title="Daily Fuel Goal"
              value={diet ? `${diet.daily_calories} kcal` : '—'}
              subtitle={diet?.title || 'Custom Diet'}
              icon={Utensils}
              accent="amber"
            />
            <StatCard
              title="Discipline Streak"
              value={`${(stats?.total_checkins_this_month || 0) > 4 ? '🔥 On Fire' : '⚡ Building'}`}
              subtitle="Keep consistent"
              icon={Award}
              accent="blue"
            />
          </div>

          {/* Quick Active Plan Overviews */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Workout Highlights */}
            <Card className="border-zinc-800 bg-[#0f0f15]">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Dumbbell className="w-5 h-5 text-red-500" /> Current Workout Program
                  </CardTitle>
                  <p className="text-xs text-zinc-400">{workout?.title || 'No active routine assigned'}</p>
                </div>
                <Badge variant="rage">{workout?.goal || 'Strength'}</Badge>
              </CardHeader>
              <CardContent>
                {workout ? (
                  <div className="space-y-3">
                    <div className="p-3 rounded-lg bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300">
                      <strong className="text-red-400">Coach:</strong> {workout.trainer_name} • Started on {workout.start_date}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {workout.exercises_schedule?.slice(0, 2).map((day, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 text-xs">
                          <span className="font-bold text-red-400 block mb-1">{day.day}</span>
                          <span className="text-zinc-400 text-[11px]">{day.exercises?.length} Exercises Scheduled</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">Your coach will assign your personalized split shortly.</p>
                )}
              </CardContent>
            </Card>

            {/* Nutrition Highlights */}
            <Card className="border-zinc-800 bg-[#0f0f15]">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Utensils className="w-5 h-5 text-emerald-400" /> Nutrition & Macros Target
                  </CardTitle>
                  <p className="text-xs text-zinc-400">{diet?.title || 'No custom meal plan'}</p>
                </div>
                <Badge variant="success">{diet?.daily_calories || 0} KCAL</Badge>
              </CardHeader>
              <CardContent>
                {diet ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 uppercase font-bold block">Protein</span>
                        <span className="text-sm font-bold text-red-400">{diet.macros?.protein || '—'}</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 uppercase font-bold block">Carbs</span>
                        <span className="text-sm font-bold text-amber-400">{diet.macros?.carbs || '—'}</span>
                      </div>
                      <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800">
                        <span className="text-[10px] text-zinc-400 uppercase font-bold block">Fats</span>
                        <span className="text-sm font-bold text-emerald-400">{diet.macros?.fats || '—'}</span>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-400 italic">"{diet.guidelines}"</p>
                  </div>
                ) : (
                  <p className="text-xs text-zinc-500 italic">Nutrition protocol not assigned yet.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* 2. WORKOUT SCHEDULE TAB */}
      {currentTab === 'member-workout' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Assigned Workout Schedule</h2>
              <p className="text-xs text-zinc-400">Exercise breakdown, sets, rep targets, and rest tempos</p>
            </div>
            {workout && <Badge variant="rage">{workout.goal}</Badge>}
          </div>

          {workout ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-[#111117] border border-zinc-800 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-white text-base">{workout.title}</h3>
                  <p className="text-xs text-zinc-400">Created by Coach <strong className="text-zinc-200">{workout.trainer_name}</strong></p>
                </div>
                <Badge variant="success">Active Program</Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {workout.exercises_schedule?.map((day, didx) => (
                  <Card key={didx} className="border-zinc-800 bg-[#0f0f15]">
                    <h4 className="font-bold text-red-500 text-sm uppercase tracking-wider mb-3 pb-2 border-b border-zinc-800">
                      {day.day}
                    </h4>
                    <div className="space-y-3">
                      {day.exercises?.map((ex, eidx) => (
                        <div key={eidx} className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80 text-xs">
                          <div className="font-bold text-white text-sm">{ex.name}</div>
                          <div className="text-red-400 font-mono font-bold text-xs mt-1">
                            {ex.sets} Sets × {ex.reps} Reps
                          </div>
                          {ex.rest && <div className="text-zinc-400 text-[11px] mt-0.5">⏱ Rest: {ex.rest}</div>}
                          {ex.notes && <div className="text-zinc-500 text-[10px] mt-1 italic">💡 {ex.notes}</div>}
                        </div>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ) : (
            <Card className="text-center p-8 border-zinc-800">
              <Dumbbell className="w-10 h-10 text-zinc-600 mx-auto mb-2" />
              <h3 className="font-bold text-white text-base">No Workout Routine Assigned</h3>
              <p className="text-xs text-zinc-400 mt-1">Please ask your gym coach to assign a workout split to your profile.</p>
            </Card>
          )}
        </div>
      )}

      {/* 3. DIET & NUTRITION TAB */}
      {currentTab === 'member-diet' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Nutrition Program & Meal Timing</h2>
              <p className="text-xs text-zinc-400">Daily calorie targets and structured meal timetable</p>
            </div>
            {diet && <Badge variant="rage">{diet.daily_calories} Total KCAL</Badge>}
          </div>

          {diet ? (
            <div className="space-y-4">
              {/* Macros Summary Bar */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="p-4 rounded-xl bg-[#111117] border border-zinc-800 text-center">
                  <span className="text-xs text-zinc-400 uppercase font-bold">Calories</span>
                  <div className="text-xl font-black text-white mt-1">{diet.daily_calories} kcal</div>
                </div>
                <div className="p-4 rounded-xl bg-[#111117] border border-red-900/30 text-center">
                  <span className="text-xs text-red-400 uppercase font-bold">Protein</span>
                  <div className="text-xl font-black text-white mt-1">{diet.macros?.protein || '—'}</div>
                </div>
                <div className="p-4 rounded-xl bg-[#111117] border border-amber-900/30 text-center">
                  <span className="text-xs text-amber-400 uppercase font-bold">Carbs</span>
                  <div className="text-xl font-black text-white mt-1">{diet.macros?.carbs || '—'}</div>
                </div>
                <div className="p-4 rounded-xl bg-[#111117] border border-emerald-900/30 text-center">
                  <span className="text-xs text-emerald-400 uppercase font-bold">Fats</span>
                  <div className="text-xl font-black text-white mt-1">{diet.macros?.fats || '—'}</div>
                </div>
              </div>

              {/* Meals List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {diet.meals_schedule?.map((meal, midx) => (
                  <Card key={midx} className="border-zinc-800 bg-[#0f0f15]">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono font-bold text-emerald-400">{meal.time}</span>
                      <Badge variant="outline">{meal.calories} kcal</Badge>
                    </div>
                    <h4 className="font-bold text-white text-base mb-1">{meal.meal_name}</h4>
                    <p className="text-xs text-zinc-300 p-2.5 rounded-lg bg-zinc-900/70 border border-zinc-800">
                      {meal.items}
                    </p>
                    <div className="mt-2 text-[11px] text-zinc-400 font-mono">
                      P: {meal.protein} • C: {meal.carbs} • F: {meal.fats}
                    </div>
                  </Card>
                ))}
              </div>

              {diet.guidelines && (
                <div className="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-300">
                  <strong className="text-red-400">Trainer Nutrition Notes:</strong> {diet.guidelines}
                </div>
              )}
            </div>
          ) : (
            <Card className="text-center p-8 border-zinc-800">
              <Utensils className="w-10 h-10 text-zinc-600 mx-auto mb-2" />
              <h3 className="font-bold text-white text-base">No Meal Plan Assigned</h3>
              <p className="text-xs text-zinc-400 mt-1">Your nutrition plan will appear here once configured by your coach.</p>
            </Card>
          )}
        </div>
      )}

      {/* 4. ATTENDANCE LOGS TAB */}
      {currentTab === 'member-attendance' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Personal Gym Attendance History</h2>
            <p className="text-xs text-zinc-400">Complete log of your facility check-in and check-out timestamps</p>
          </div>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Check-In Time</th>
                  <th className="px-4 py-3">Check-Out Time</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Session Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {attendances?.map((att) => (
                  <tr key={att.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-mono font-bold text-white">{att.date}</td>
                    <td className="px-4 py-3 text-emerald-400 font-mono font-bold">{att.check_in_time}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{att.check_out_time || 'Session Completed'}</td>
                    <td className="px-4 py-3"><Badge variant="success">{att.status}</Badge></td>
                    <td className="px-4 py-3 text-zinc-400">{att.notes || 'Workout completed'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* 5. PLAN & INVOICES TAB */}
      {currentTab === 'member-subscription' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Membership Plan & Invoices</h2>
            <p className="text-xs text-zinc-400">Review subscription validity, invoice history, and payment receipts</p>
          </div>

          <Card className="border-zinc-800 bg-[#101017]">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
              <div>
                <h3 className="text-lg font-bold text-white">{subscription?.plan_name || 'Standard Pass'}</h3>
                <p className="text-xs text-zinc-400">Valid: <strong className="text-zinc-200">{subscription?.start_date}</strong> to <strong className="text-zinc-200">{subscription?.end_date}</strong></p>
              </div>
              <Badge variant={subscription?.status === 'active' ? 'success' : 'danger'}>
                {subscription?.status}
              </Badge>
            </div>
            <div className="mt-4 flex items-center justify-between text-xs">
              <span className="text-zinc-400">Remaining Period:</span>
              <span className="text-emerald-400 font-bold font-mono text-sm">{subscription?.days_left ?? 0} Days</span>
            </div>
          </Card>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <div className="p-4 border-b border-zinc-800">
              <h3 className="font-bold text-white text-sm">Receipts & Transaction Invoices</h3>
            </div>
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Invoice Number</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Payment Method</th>
                  <th className="px-4 py-3">Transaction Date</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {payments?.map((pay) => (
                  <tr key={pay.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-mono font-bold text-red-400">{pay.invoice_number}</td>
                    <td className="px-4 py-3 font-bold text-white font-mono">₹{pay.amount.toLocaleString('en-IN')}</td>
                    <td className="px-4 py-3 uppercase text-zinc-400">{pay.payment_method}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{new Date(pay.transaction_date).toLocaleDateString()}</td>
                    <td className="px-4 py-3"><Badge variant="success">{pay.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </div>
  );
};
