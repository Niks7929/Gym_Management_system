import React, { useState } from 'react';
import {
  useTrainerAnalyticsQuery, useTrainerClientsQuery, useWorkoutsQuery,
  useDietsQuery, useCreateWorkoutMutation, useCreateDietMutation,
  useUsersQuery, useAttendancesQuery
} from '../../api/queries';
import {
  Dumbbell, Utensils, Users, CalendarCheck, Plus, CheckCircle
} from 'lucide-react';
import {
  Card, StatCard,
  Button, Badge, Modal, Input, Select
} from '../../components/ui';

interface TrainerPortalProps {
  currentTab: string;
}

export const TrainerPortal: React.FC<TrainerPortalProps> = ({ currentTab }) => {
  const { data: stats } = useTrainerAnalyticsQuery();
  const { data: clients } = useTrainerClientsQuery();
  const { data: workouts } = useWorkoutsQuery();
  const { data: diets } = useDietsQuery();
  const { data: members } = useUsersQuery({ role: 'member' });
  const { data: attendances } = useAttendancesQuery();

  const createWorkoutMutation = useCreateWorkoutMutation();
  const createDietMutation = useCreateDietMutation();

  const [isWorkoutModalOpen, setIsWorkoutModalOpen] = useState(false);
  const [isDietModalOpen, setIsDietModalOpen] = useState(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Workout Builder Form
  const [workoutForm, setWorkoutForm] = useState({
    member_id: members?.[0]?.id || 1,
    title: '',
    goal: 'Hypertrophy & Strength',
    day1_name: 'Day 1: Upper Body Push',
    day1_ex1: 'Barbell Incline Bench Press',
    day1_sets1: '4',
    day1_reps1: '8-10',
    day1_ex2: 'Flat Dumbbell Press',
    day1_sets2: '3',
    day1_reps2: '10-12',
    day2_name: 'Day 2: Back & Pull',
    day2_ex1: 'Conventional Deadlift',
    day2_sets1: '4',
    day2_reps1: '5',
    day2_ex2: 'Lat Pulldown',
    day2_sets2: '3',
    day2_reps2: '12',
  });

  // Diet Builder Form
  const [dietForm, setDietForm] = useState({
    member_id: members?.[0]?.id || 1,
    title: '',
    daily_calories: 2500,
    protein: '180g',
    carbs: '260g',
    fats: '65g',
    guidelines: 'Stay hydrated with 3.5L water. Take post-workout protein shake with 5g creatine.',
    breakfast: '4 Eggs, 80g Oats with Berries & Peanut Butter',
    lunch: '200g Grilled Chicken Breast, 200g Jasmine Rice, Asparagus',
    snack: 'Greek Yogurt with Handful of Almonds & 1 Banana',
    dinner: '200g Salmon Fillet, Baked Sweet Potato, Green Salad',
  });

  const handleCreateWorkout = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const schedule = [
        {
          day: workoutForm.day1_name,
          exercises: [
            { name: workoutForm.day1_ex1, sets: workoutForm.day1_sets1, reps: workoutForm.day1_reps1, notes: 'Strict form' },
            { name: workoutForm.day1_ex2, sets: workoutForm.day1_sets2, reps: workoutForm.day1_reps2, notes: 'Deep stretch' },
          ],
        },
        {
          day: workoutForm.day2_name,
          exercises: [
            { name: workoutForm.day2_ex1, sets: workoutForm.day2_sets1, reps: workoutForm.day2_reps1, notes: 'Explosive drive' },
            { name: workoutForm.day2_ex2, sets: workoutForm.day2_sets2, reps: workoutForm.day2_reps2, notes: 'Squeeze lats' },
          ],
        },
      ];

      await createWorkoutMutation.mutateAsync({
        member_id: Number(workoutForm.member_id),
        title: workoutForm.title,
        goal: workoutForm.goal,
        exercises_schedule: schedule,
      });

      setIsWorkoutModalOpen(false);
      setSuccessNotice(`Workout routine "${workoutForm.title}" assigned successfully!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create workout plan');
    }
  };

  const handleCreateDiet = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const meals = [
        { time: '08:00 AM - Breakfast', meal_name: 'Power Breakfast', items: dietForm.breakfast, calories: 650, protein: '45g', carbs: '65g', fats: '18g' },
        { time: '01:00 PM - Lunch', meal_name: 'Main Fuel Lunch', items: dietForm.lunch, calories: 750, protein: '55g', carbs: '75g', fats: '16g' },
        { time: '04:30 PM - Snack', meal_name: 'Pre-Workout Energy', items: dietForm.snack, calories: 350, protein: '25g', carbs: '40g', fats: '10g' },
        { time: '08:00 PM - Dinner', meal_name: 'Recovery Dinner', items: dietForm.dinner, calories: 650, protein: '45g', carbs: '50g', fats: '22g' },
      ];

      await createDietMutation.mutateAsync({
        member_id: Number(dietForm.member_id),
        title: dietForm.title,
        daily_calories: Number(dietForm.daily_calories),
        macros: { protein: dietForm.protein, carbs: dietForm.carbs, fats: dietForm.fats },
        meals_schedule: meals,
        guidelines: dietForm.guidelines,
      });

      setIsDietModalOpen(false);
      setSuccessNotice(`Diet plan "${dietForm.title}" assigned successfully!`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create diet plan');
    }
  };

  return (
    <div className="space-y-6">
      {successNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-700 text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span>{successNotice}</span>
          </div>
          <button onClick={() => setSuccessNotice(null)} className="text-emerald-400 hover:text-white font-bold">✕</button>
        </div>
      )}

      {/* 1. COACH DASHBOARD OVERVIEW */}
      {(currentTab === 'trainer-dashboard' || !currentTab) && (
        <div className="space-y-6">
          <div>
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
              <span>Coach Command Center</span>
              <Badge variant="warning">Trainer</Badge>
            </h1>
            <p className="text-xs text-zinc-400 mt-1">Client rosters, customized workout schedules, and macro nutrition regimens</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Assigned Clients"
              value={stats?.assigned_clients_count || 0}
              subtitle="Active 1-on-1 athletes"
              icon={Users}
              accent="amber"
            />
            <StatCard
              title="Active Workouts"
              value={stats?.active_workouts_count || 0}
              subtitle="Custom split routines created"
              icon={Dumbbell}
              accent="rage"
            />
            <StatCard
              title="Active Diet Plans"
              value={stats?.active_diets_count || 0}
              subtitle="Nutritional meal programs"
              icon={Utensils}
              accent="emerald"
            />
            <StatCard
              title="Client Check-ins Today"
              value={stats?.today_client_checkins || 0}
              subtitle="Clients training in gym today"
              icon={CalendarCheck}
              accent="blue"
            />
          </div>

          {/* Quick Shortcuts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="border-red-900/40 bg-[#121219] p-5 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-base flex items-center gap-2">
                  <Dumbbell className="w-5 h-5 text-red-500" /> Build Workout Split
                </h3>
                <p className="text-xs text-zinc-400 mt-1">Construct exercises, rep ranges, and sets for your athletes</p>
              </div>
              <Button variant="rage" size="sm" onClick={() => setIsWorkoutModalOpen(true)}>
                <Plus className="w-4 h-4" /> New Routine
              </Button>
            </Card>

            <Card className="border-emerald-900/40 bg-[#121219] p-5 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-base flex items-center gap-2">
                  <Utensils className="w-5 h-5 text-emerald-400" /> Build Nutrition Plan
                </h3>
                <p className="text-xs text-zinc-400 mt-1">Configure daily calorie targets, macros, and scheduled meals</p>
              </div>
              <Button variant="rage" size="sm" onClick={() => setIsDietModalOpen(true)}>
                <Plus className="w-4 h-4" /> New Meal Plan
              </Button>
            </Card>
          </div>
        </div>
      )}

      {/* 2. ASSIGNED CLIENTS TAB */}
      {currentTab === 'trainer-clients' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Assigned Athlete Roster</h2>
              <p className="text-xs text-zinc-400">Track client subscription validity, program goals, and contact info</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clients?.map((client) => (
              <Card key={client.id} className="border-zinc-800 bg-[#0f0f15]">
                <div className="flex items-center justify-between mb-3">
                  <Badge variant="warning">{client.active_plan_name}</Badge>
                  <span className="text-xs text-emerald-400 font-mono font-bold">
                    {client.days_left_in_membership} Days Left
                  </span>
                </div>
                <h3 className="text-lg font-bold text-white">{client.member_name}</h3>
                <p className="text-xs text-zinc-400 font-mono">{client.member_email}</p>
                <p className="text-xs text-zinc-400 font-mono">{client.member_phone}</p>
                <p className="text-xs text-zinc-300 mt-3 p-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800">
                  💬 {client.notes || 'Training for overall strength and body recomposition.'}
                </p>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 3. WORKOUT BUILDER TAB */}
      {currentTab === 'trainer-workouts' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Workout Routine Programs</h2>
              <p className="text-xs text-zinc-400">Assigned exercise routines, split schedules, and volume protocols</p>
            </div>
            <Button variant="rage" onClick={() => setIsWorkoutModalOpen(true)}>
              <Plus className="w-4 h-4" /> Build Custom Routine
            </Button>
          </div>

          <div className="space-y-4">
            {workouts?.map((w) => (
              <Card key={w.id} className="border-zinc-800 bg-[#101017]">
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-zinc-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-white">{w.title}</h3>
                      <Badge variant="rage">{w.goal}</Badge>
                    </div>
                    <p className="text-xs text-zinc-400 mt-0.5">Assigned to: <strong className="text-zinc-200">{w.member_name}</strong></p>
                  </div>
                  <Badge variant="success">Active Protocol</Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {w.exercises_schedule?.map((day: any, didx: number) => (
                    <div key={didx} className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800">
                      <h4 className="font-bold text-red-400 text-xs uppercase tracking-wider mb-2.5">{day.day}</h4>
                      <div className="space-y-2">
                        {day.exercises?.map((ex: any, eidx: number) => (
                          <div key={eidx} className="text-xs border-b border-zinc-800/40 pb-1.5 last:border-0">
                            <div className="font-semibold text-zinc-200">{ex.name}</div>
                            <div className="text-zinc-400 text-[11px] font-mono">
                              {ex.sets} Sets × {ex.reps} Reps {ex.rest ? `• Rest ${ex.rest}` : ''}
                            </div>
                            {ex.notes && <div className="text-zinc-500 text-[10px] italic">{ex.notes}</div>}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 4. NUTRITION & DIETS TAB */}
      {currentTab === 'trainer-diets' && (
        <div className="space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Nutrition & Diet Protocols</h2>
              <p className="text-xs text-zinc-400">Meal timing, macronutrient targets, and dietary guidelines</p>
            </div>
            <Button variant="rage" onClick={() => setIsDietModalOpen(true)}>
              <Plus className="w-4 h-4" /> Create Nutrition Plan
            </Button>
          </div>

          <div className="space-y-4">
            {diets?.map((d) => (
              <Card key={d.id} className="border-zinc-800 bg-[#101017]">
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-zinc-800">
                  <div>
                    <h3 className="text-lg font-bold text-white">{d.title}</h3>
                    <p className="text-xs text-zinc-400">Client: <strong className="text-zinc-200">{d.member_name}</strong></p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="rage">{d.daily_calories} KCAL</Badge>
                    <Badge variant="outline">P: {d.macros?.protein || '—'} | C: {d.macros?.carbs || '—'} | F: {d.macros?.fats || '—'}</Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
                  {d.meals_schedule?.map((meal: any, midx: number) => (
                    <div key={midx} className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs">
                      <div className="font-bold text-emerald-400 text-[11px] mb-1">{meal.time}</div>
                      <div className="font-semibold text-zinc-200">{meal.meal_name}</div>
                      <p className="text-zinc-400 text-[11px] mt-1">{meal.items}</p>
                    </div>
                  ))}
                </div>

                {d.guidelines && (
                  <p className="text-xs text-zinc-400 bg-zinc-950/80 p-3 rounded-lg border border-zinc-800">
                    💡 <strong className="text-zinc-300">Guidelines:</strong> {d.guidelines}
                  </p>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 5. CLIENT ATTENDANCE TAB */}
      {currentTab === 'trainer-attendance' && (
        <div className="space-y-5">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Client Session Logs</h2>
            <p className="text-xs text-zinc-400">Track check-ins and session compliance for your athletes</p>
          </div>

          <Card className="overflow-x-auto p-0 border-zinc-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#14141c] text-zinc-400 uppercase border-b border-zinc-800">
                <tr>
                  <th className="px-4 py-3">Client</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Check-In</th>
                  <th className="px-4 py-3">Check-Out</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Session Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/60">
                {attendances?.map((att) => (
                  <tr key={att.id} className="hover:bg-zinc-800/30">
                    <td className="px-4 py-3 font-bold text-white">{att.member_name}</td>
                    <td className="px-4 py-3 text-zinc-300 font-mono">{att.date}</td>
                    <td className="px-4 py-3 text-emerald-400 font-mono font-bold">{att.check_in_time}</td>
                    <td className="px-4 py-3 text-zinc-400 font-mono">{att.check_out_time || 'Active Session'}</td>
                    <td className="px-4 py-3"><Badge variant="success">{att.status}</Badge></td>
                    <td className="px-4 py-3 text-zinc-400">{att.notes || 'Routine completed'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* MODAL: BUILD WORKOUT ROUTINE */}
      <Modal
        isOpen={isWorkoutModalOpen}
        onClose={() => setIsWorkoutModalOpen(false)}
        title="Create Custom Workout Routine"
        description="Assign a multi-day training split to your client"
      >
        <form onSubmit={handleCreateWorkout} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Target Client</label>
              <Select
                value={workoutForm.member_id}
                onChange={(e) => setWorkoutForm({ ...workoutForm, member_id: Number(e.target.value) })}
              >
                {members?.map((m) => (
                  <option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>
                ))}
              </Select>
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Primary Goal</label>
              <Input
                value={workoutForm.goal}
                onChange={(e) => setWorkoutForm({ ...workoutForm, goal: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Routine Title</label>
            <Input
              required
              placeholder="e.g. 4-Day Strength & Hypertrophy Protocol"
              value={workoutForm.title}
              onChange={(e) => setWorkoutForm({ ...workoutForm, title: e.target.value })}
            />
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900/70 border border-zinc-800 space-y-2">
            <h4 className="text-xs font-bold uppercase text-red-400">Day 1 Routine</h4>
            <Input
              placeholder="Day 1 Title (e.g. Upper Body Push)"
              value={workoutForm.day1_name}
              onChange={(e) => setWorkoutForm({ ...workoutForm, day1_name: e.target.value })}
            />
            <div className="grid grid-cols-3 gap-2">
              <Input
                placeholder="Exercise 1"
                value={workoutForm.day1_ex1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day1_ex1: e.target.value })}
              />
              <Input
                placeholder="Sets (e.g. 4)"
                value={workoutForm.day1_sets1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day1_sets1: e.target.value })}
              />
              <Input
                placeholder="Reps (e.g. 8-10)"
                value={workoutForm.day1_reps1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day1_reps1: e.target.value })}
              />
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900/70 border border-zinc-800 space-y-2">
            <h4 className="text-xs font-bold uppercase text-red-400">Day 2 Routine</h4>
            <Input
              placeholder="Day 2 Title (e.g. Pull & Deadlift)"
              value={workoutForm.day2_name}
              onChange={(e) => setWorkoutForm({ ...workoutForm, day2_name: e.target.value })}
            />
            <div className="grid grid-cols-3 gap-2">
              <Input
                placeholder="Exercise 1"
                value={workoutForm.day2_ex1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day2_ex1: e.target.value })}
              />
              <Input
                placeholder="Sets (e.g. 4)"
                value={workoutForm.day2_sets1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day2_sets1: e.target.value })}
              />
              <Input
                placeholder="Reps (e.g. 5)"
                value={workoutForm.day2_reps1}
                onChange={(e) => setWorkoutForm({ ...workoutForm, day2_reps1: e.target.value })}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsWorkoutModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={createWorkoutMutation.isPending}>
              Assign Workout Plan
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: BUILD DIET PLAN */}
      <Modal
        isOpen={isDietModalOpen}
        onClose={() => setIsDietModalOpen(false)}
        title="Create Customized Nutrition Plan"
        description="Configure calories, macros and meal timings"
      >
        <form onSubmit={handleCreateDiet} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Target Client</label>
              <Select
                value={dietForm.member_id}
                onChange={(e) => setDietForm({ ...dietForm, member_id: Number(e.target.value) })}
              >
                {members?.map((m) => (
                  <option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>
                ))}
              </Select>
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Daily Calories (kcal)</label>
              <Input
                type="number"
                value={dietForm.daily_calories}
                onChange={(e) => setDietForm({ ...dietForm, daily_calories: Number(e.target.value) })}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-1">Diet Program Title</label>
            <Input
              required
              placeholder="e.g. High-Protein Lean Bulk Regimen"
              value={dietForm.title}
              onChange={(e) => setDietForm({ ...dietForm, title: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Protein</label>
              <Input
                value={dietForm.protein}
                onChange={(e) => setDietForm({ ...dietForm, protein: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Carbs</label>
              <Input
                value={dietForm.carbs}
                onChange={(e) => setDietForm({ ...dietForm, carbs: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">Fats</label>
              <Input
                value={dietForm.fats}
                onChange={(e) => setDietForm({ ...dietForm, fats: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-zinc-300">Meals Schedule</label>
            <Input
              placeholder="Breakfast items"
              value={dietForm.breakfast}
              onChange={(e) => setDietForm({ ...dietForm, breakfast: e.target.value })}
            />
            <Input
              placeholder="Lunch items"
              value={dietForm.lunch}
              onChange={(e) => setDietForm({ ...dietForm, lunch: e.target.value })}
            />
            <Input
              placeholder="Snack items"
              value={dietForm.snack}
              onChange={(e) => setDietForm({ ...dietForm, snack: e.target.value })}
            />
            <Input
              placeholder="Dinner items"
              value={dietForm.dinner}
              onChange={(e) => setDietForm({ ...dietForm, dinner: e.target.value })}
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsDietModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="rage" isLoading={createDietMutation.isPending}>
              Assign Nutrition Plan
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
