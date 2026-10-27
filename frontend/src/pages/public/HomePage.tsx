import React, { useState, useEffect } from 'react';
import { usePlansQuery, useBranchesQuery, useGymSettingsQuery, useCreateEnquiryMutation } from '../../api/queries';
import {
  Flame, Dumbbell, Utensils, Shield, MapPin,
  CheckCircle, ArrowRight, Phone, Mail, ChevronRight, Zap,
  ChevronLeft, MessageSquare, Send, CheckCircle2, AlertCircle, Sparkles
} from 'lucide-react';
import { Button, Badge, Card, Input, Select } from '../../components/ui';
import { ThemeToggle } from '../../components/ThemeToggle';

interface HomePageProps {
  onNavigateLogin: () => void;
  onNavigateRegister: (planId?: number) => void;
  onNavigateAdminControl?: () => void;
}

const HERO_SLIDES = [
  {
    image: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop',
    title: 'TRANSFORM YOUR POWER',
    subtitle: 'High-performance strength, master coaching, and elite powerlifting facilities.',
  },
  {
    image: 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=2070&auto=format&fit=crop',
    title: 'FORGED IN DISCIPLINE',
    subtitle: 'Calibrated Olympic plates, competition racks, and state-of-the-art hypertrophy equipment.',
  },
  {
    image: 'https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=2070&auto=format&fit=crop',
    title: 'ELEVATE YOUR POTENTIAL',
    subtitle: 'Custom nutritional blueprints, 1-on-1 personal guidance, and sauna recovery therapy.',
  },
  {
    image: 'https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?q=80&w=2074&auto=format&fit=crop',
    title: '24/7 MULTI-BRANCH ACCESS',
    subtitle: 'Unrestricted keycard entry across metropolitan titanium gym network.',
  },
];

export const HomePage: React.FC<HomePageProps> = ({
  onNavigateLogin,
  onNavigateRegister,
  onNavigateAdminControl,
}) => {
  const { data: plans } = usePlansQuery();
  const { data: branches } = useBranchesQuery();
  const { data: settings } = useGymSettingsQuery();
  const createEnquiryMutation = useCreateEnquiryMutation();

  const [currentSlide, setCurrentSlide] = useState(0);

  // Enquiry Lead Form State
  const [enquiryForm, setEnquiryForm] = useState({
    name: '',
    phone: '',
    email: '',
    preferred_branch_id: '',
    fitness_goal: 'muscle_building',
    notes: '',
  });
  const [enquirySuccess, setEnquirySuccess] = useState(false);
  const [enquiryError, setEnquiryError] = useState('');

  const handleEnquirySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEnquiryError('');
    if (!enquiryForm.name || !enquiryForm.phone) {
      setEnquiryError('Please provide your name and phone number.');
      return;
    }
    try {
      await createEnquiryMutation.mutateAsync({
        name: enquiryForm.name,
        phone: enquiryForm.phone,
        email: enquiryForm.email || undefined,
        preferred_branch_id: enquiryForm.preferred_branch_id ? Number(enquiryForm.preferred_branch_id) : undefined,
        fitness_goal: enquiryForm.fitness_goal,
        notes: enquiryForm.notes || undefined,
      });
      setEnquirySuccess(true);
      setEnquiryForm({
        name: '',
        phone: '',
        email: '',
        preferred_branch_id: '',
        fitness_goal: 'muscle_building',
        notes: '',
      });
    } catch (err: any) {
      setEnquiryError(err.response?.data?.detail || 'Failed to submit enquiry. Please try again.');
    }
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 5500);
    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % HERO_SLIDES.length);
  const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + HERO_SLIDES.length) % HERO_SLIDES.length);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#040406] text-slate-900 dark:text-zinc-100 font-sans transition-colors duration-200">
      {/* 1. TOP ANNOUNCEMENT BAR */}
      {settings?.announcement_bar && (
        <div className="bg-slate-900 dark:bg-[#09090e] border-b border-slate-800 dark:border-white/10 px-4 py-2 text-center text-xs text-white">
          <span className="font-black uppercase tracking-wider mr-2 px-2 py-0.5 rounded bg-white/10 border border-white/20 text-[10px]">
            ⚡ ANNOUNCEMENT
          </span>
          {settings.announcement_bar}
        </div>
      )}

      {/* 2. NAVIGATION HEADER */}
      <header className="sticky top-0 z-50 bg-white/90 dark:bg-[#060609]/90 backdrop-blur-xl border-b border-slate-200 dark:border-white/10 px-4 sm:px-8 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center shadow-sm">
              <Flame className="w-6 h-6 text-current" />
            </div>
            <div>
              <span className="font-black text-2xl tracking-widest text-slate-900 dark:text-white">SETFIT</span>
              <span className="text-[10px] ml-2 px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-900 text-slate-700 dark:text-zinc-300 font-mono font-black border border-slate-200 dark:border-white/15 uppercase tracking-widest">
                ELITE
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-xs uppercase tracking-widest font-bold text-slate-600 dark:text-zinc-400">
            <a href="#features" className="hover:text-black dark:hover:text-white transition-colors">Features</a>
            <a href="#plans" className="hover:text-black dark:hover:text-white transition-colors">Memberships</a>
            <a href="#assessment" className="hover:text-black dark:hover:text-white transition-colors text-amber-500 font-black">Free Assessment</a>
            <a href="#trainers" className="hover:text-black dark:hover:text-white transition-colors">Coaches</a>
            <a href="#branches" className="hover:text-black dark:hover:text-white transition-colors">Locations</a>
          </nav>

          <div className="flex items-center gap-3">
            {/* Theme Toggle Sun/Moon */}
            <ThemeToggle />

            <Button
              variant="outline"
              size="sm"
              onClick={onNavigateLogin}
              className="text-xs uppercase font-bold"
            >
              Sign In
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => onNavigateRegister()}
              className="text-xs uppercase font-black"
            >
              Join Now <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </header>

      {/* 3. HERO SECTION WITH IMAGE SLIDER & "TRANSFORM YOUR POWER" */}
      <section className="relative min-h-[88vh] flex items-center justify-center px-4 sm:px-8 overflow-hidden">
        {/* Background Image Carousel Layers */}
        {HERO_SLIDES.map((slide, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${
              index === currentSlide ? 'opacity-100 scale-100 z-0' : 'opacity-0 scale-105 pointer-events-none'
            }`}
          >
            <img
              src={slide.image}
              alt={slide.title}
              className="w-full h-full object-cover object-center filter brightness-75 contrast-110 dark:grayscale dark:contrast-125 dark:brightness-60"
            />
            {/* Theme-Adaptive Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/70 to-slate-900/40 dark:from-[#040406] dark:via-[#040406]/85 dark:to-[#040406]/60" />
          </div>
        ))}

        {/* Carousel Slide Indicators */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-2">
          {HERO_SLIDES.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentSlide(idx)}
              className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${
                idx === currentSlide ? 'w-8 bg-white shadow-sm' : 'w-2 bg-white/30 hover:bg-white/60'
              }`}
              aria-label={`Go to slide ${idx + 1}`}
            />
          ))}
        </div>

        {/* Carousel Controls */}
        <button
          onClick={prevSlide}
          className="absolute left-4 sm:left-8 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-black/50 hover:bg-black/80 text-white border border-white/20 flex items-center justify-center transition-all cursor-pointer backdrop-blur-md"
          aria-label="Previous Slide"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-4 sm:right-8 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-black/50 hover:bg-black/80 text-white border border-white/20 flex items-center justify-center transition-all cursor-pointer backdrop-blur-md"
          aria-label="Next Slide"
        >
          <ChevronRight className="w-5 h-5" />
        </button>

        {/* Hero Content */}
        <div className="max-w-4xl mx-auto text-center relative z-10 py-16 space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-black/70 border border-white/25 text-white text-xs font-black uppercase tracking-widest backdrop-blur-md shadow-sm">
            <Zap className="w-3.5 h-3.5 text-yellow-400" />
            FORGED IN IRON • POWERED BY DISCIPLINE
          </div>

          {/* Prominent Slogan / Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black text-white tracking-tight leading-[1.05] uppercase drop-shadow-md">
            TRANSFORM YOUR POWER
          </h1>

          <p className="text-base sm:text-lg text-slate-200 max-w-2xl mx-auto font-normal leading-relaxed drop-shadow-sm">
            Welcome to <strong className="text-white font-bold">SETFIT</strong> — the premier high-performance strength and conditioning facility. Master-level coaching, Olympic powerlifting equipment, and tailor-made nutrition plans.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Button
              variant="primary"
              size="lg"
              onClick={() => onNavigateRegister()}
              className="w-full sm:w-auto text-sm uppercase px-8 py-4 font-black bg-white text-black hover:bg-slate-100 shadow-lg cursor-pointer"
            >
              Claim Membership Pass <ArrowRight className="w-4 h-4" />
            </Button>
            <Button
              variant="secondary"
              size="lg"
              onClick={onNavigateLogin}
              className="w-full sm:w-auto text-sm uppercase px-8 py-4 font-bold bg-black/60 text-white hover:bg-black/90 border border-white/25 backdrop-blur-md cursor-pointer"
            >
              Portal Sign In
            </Button>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-10 border-t border-white/20 mt-10">
            <div className="p-4 rounded-2xl bg-black/60 border border-white/15 backdrop-blur-md">
              <div className="text-2xl sm:text-3xl font-black text-white font-mono">24/7</div>
              <p className="text-[11px] text-slate-300 uppercase tracking-widest font-bold mt-1">Keycard Access</p>
            </div>
            <div className="p-4 rounded-2xl bg-black/60 border border-white/15 backdrop-blur-md">
              <div className="text-2xl sm:text-3xl font-black text-white font-mono">100%</div>
              <p className="text-[11px] text-slate-300 uppercase tracking-widest font-bold mt-1">Olympic Gear</p>
            </div>
            <div className="p-4 rounded-2xl bg-black/60 border border-white/15 backdrop-blur-md">
              <div className="text-2xl sm:text-3xl font-black text-white font-mono">15+</div>
              <p className="text-[11px] text-slate-300 uppercase tracking-widest font-bold mt-1">Master Coaches</p>
            </div>
            <div className="p-4 rounded-2xl bg-black/60 border border-white/15 backdrop-blur-md">
              <div className="text-2xl sm:text-3xl font-black text-white font-mono">5,000+</div>
              <p className="text-[11px] text-slate-300 uppercase tracking-widest font-bold mt-1">Transformations</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FACILITY FEATURES */}
      <section id="features" className="py-24 px-4 sm:px-8 bg-white dark:bg-[#07070a] border-t border-slate-200 dark:border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <Badge variant="white">The SETFIT Standard</Badge>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              Engineered for Maximum Strength & Recovery
            </h2>
            <p className="text-xs uppercase tracking-widest text-slate-500 dark:text-zinc-400">
              Elite facilities built to exceed physical and mental limits.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-7">
              <div className="w-12 h-12 rounded-2xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center mb-5 shadow-sm">
                <Dumbbell className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2 uppercase">Heavy Strength Arena</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Olympic lifting platforms, Eleiko calibrated plates, competition benches, and custom dumbbell pairs up to 150 lbs.
              </p>
            </Card>

            <Card className="p-7">
              <div className="w-12 h-12 rounded-2xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center mb-5 shadow-sm">
                <Utensils className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2 uppercase">Targeted Nutrition Coaching</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Personalized macro distribution (protein, carbs, fats), daily caloric targets, and scheduled meal plans designed specifically for your goals.
              </p>
            </Card>

            <Card className="p-7">
              <div className="w-12 h-12 rounded-2xl bg-slate-900 text-white dark:bg-white dark:text-black flex items-center justify-center mb-5 shadow-sm">
                <Shield className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2 uppercase">Sauna & Cold Hydrotherapy</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Infrared Finnish sauna, cold plunge tubs, and private luxury locker rooms to accelerate muscle recovery and reduce fatigue.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* 5. MEMBERSHIP PLANS & PRICING IN INDIAN RUPEES (₹ / INR) */}
      <section id="plans" className="py-24 px-4 sm:px-8 bg-slate-50 dark:bg-[#040406] border-t border-slate-200 dark:border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <Badge variant="rage">Transparent Pricing</Badge>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              Select Your Championship Pass (₹ / INR)
            </h2>
            <p className="text-xs uppercase tracking-widest text-slate-500 dark:text-zinc-400">
              No hidden fees. Flexible passes from beginner athletes to elite competitors.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {plans?.map((plan) => {
              const isFeatured = plan.name.toLowerCase().includes('annual') || plan.name.toLowerCase().includes('titan') || plan.name.toLowerCase().includes('pro');
              return (
                <Card
                  key={plan.id}
                  className={`flex flex-col justify-between p-6 transition-all duration-200 ${
                    isFeatured
                      ? 'border-slate-900 dark:border-white/40 bg-white dark:bg-[#0f0f16] relative shadow-lg'
                      : 'border-slate-200 dark:border-white/10 bg-white dark:bg-[#09090d]'
                  }`}
                >
                  {isFeatured && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-900 text-white dark:bg-white dark:text-black text-[10px] font-black uppercase px-3 py-0.5 rounded-full shadow-sm">
                      Most Popular Pass
                    </div>
                  )}

                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-black uppercase font-mono text-slate-500 dark:text-zinc-400">
                        {plan.duration_type}
                      </span>
                      <span className="text-xs text-slate-400 dark:text-zinc-500 font-mono">{plan.duration_days} Days</span>
                    </div>

                    <h3 className="text-lg font-black text-slate-900 dark:text-white mb-2 uppercase">{plan.name}</h3>
                    <div className="my-3">
                      <span className="text-3xl font-black text-slate-900 dark:text-white font-mono">
                        ₹{plan.price.toLocaleString('en-IN')}
                      </span>
                      <span className="text-xs text-slate-500 dark:text-zinc-400"> / package</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-zinc-400 mb-5">{plan.description}</p>

                    <div className="space-y-2 border-t border-slate-100 dark:border-white/10 pt-4">
                      {plan.features?.map((feat, fidx) => (
                        <div key={fidx} className="flex items-start gap-2 text-xs text-slate-700 dark:text-zinc-300">
                          <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Button
                    variant={isFeatured ? 'primary' : 'secondary'}
                    size="md"
                    onClick={() => onNavigateRegister(plan.id)}
                    className="w-full mt-6 uppercase text-xs font-black"
                  >
                    Select {plan.name.split(' ')[0]} Pass <ChevronRight className="w-4 h-4" />
                  </Button>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* 6. TRAINERS */}
      <section id="trainers" className="py-24 px-4 sm:px-8 bg-white dark:bg-[#07070a] border-t border-slate-200 dark:border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <Badge variant="white">Master Coaching Staff</Badge>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              Train With World-Class Mentors
            </h2>
            <p className="text-xs uppercase tracking-widest text-slate-500 dark:text-zinc-400">
              Certified strength coaches and nutrition specialists dedicated to your goals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-7 text-center">
              <div className="w-20 h-20 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-300 dark:border-white/20 flex items-center justify-center text-slate-900 dark:text-white text-2xl font-black mx-auto mb-4">
                MV
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white uppercase">Marcus Titan</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 font-bold mb-2">Head Strength & Hypertrophy Coach</p>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                National Powerlifting Champion with 12+ years specializing in progressive overload and mass building.
              </p>
            </Card>

            <Card className="p-7 text-center">
              <div className="w-20 h-20 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-300 dark:border-white/20 flex items-center justify-center text-slate-900 dark:text-white text-2xl font-black mx-auto mb-4">
                SC
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white uppercase">Sarah Connor</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 font-bold mb-2">Functional Athletics & Conditioning</p>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Certified Strength & Conditioning Specialist focusing on agility, mobility restoration, and body fat reduction.
              </p>
            </Card>

            <Card className="p-7 text-center">
              <div className="w-20 h-20 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-300 dark:border-white/20 flex items-center justify-center text-slate-900 dark:text-white text-2xl font-black mx-auto mb-4">
                PS
              </div>
              <h3 className="text-lg font-black text-slate-900 dark:text-white uppercase">Pooja Sharma</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 font-bold mb-2">Chief Sports Nutritionist</p>
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Sports Dietetics specialist creating clinically optimized meal and hydration regimens for athletes.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* 7. LEAD GENERATION & FREE FITNESS ASSESSMENT */}
      <section id="assessment" className="py-24 px-4 sm:px-8 bg-slate-100 dark:bg-[#09090e] border-t border-slate-200 dark:border-white/10">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left pitch */}
            <div className="lg:col-span-5 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 text-xs font-black uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                Zero Commitment Trial
              </div>
              <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white uppercase tracking-tight leading-tight">
                Book Your 1-on-1 Fitness Assessment
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">
                Meet our senior coach, measure your body composition & posture analysis, and get a tailored training recommendation at zero cost.
              </p>

              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-3 text-xs text-slate-700 dark:text-zinc-300">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">✓</div>
                  <span>InBody 570 Body Fat & Muscle Mass Analysis</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-700 dark:text-zinc-300">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">✓</div>
                  <span>Mobility & Strength Diagnostic by Certified Coach</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-700 dark:text-zinc-300">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">✓</div>
                  <span>Complimentary 1-Day Full Facility & Sauna Pass</span>
                </div>
              </div>

              {/* Direct WhatsApp Instant Consultation */}
              <div className="pt-4 border-t border-slate-200 dark:border-white/10">
                <p className="text-[11px] text-slate-500 dark:text-zinc-400 font-bold uppercase tracking-wider mb-3">
                  Prefer Instant WhatsApp Chat?
                </p>
                <a
                  href="https://wa.me/919876543210?text=Hi%20SETFIT%2C%20I%20want%20to%20book%20a%20free%20gym%20assessment%20session"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider transition-colors shadow-md"
                >
                  <MessageSquare className="w-4 h-4" />
                  Chat on WhatsApp Directly
                </a>
              </div>
            </div>

            {/* Right lead capture form */}
            <div className="lg:col-span-7">
              <Card className="p-8 border-slate-300 dark:border-white/15 bg-white dark:bg-[#0c0c12] shadow-xl">
                <h3 className="text-xl font-black text-slate-900 dark:text-white uppercase mb-1">
                  Reserve Your Free Slot
                </h3>
                <p className="text-xs text-slate-500 dark:text-zinc-400 mb-6">
                  Our front-desk team will confirm your session within 15 minutes.
                </p>

                {enquirySuccess ? (
                  <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center space-y-3">
                    <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto" />
                    <h4 className="text-base font-black text-slate-900 dark:text-white uppercase">
                      Assessment Request Received!
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                      Thank you! Our facility coach will reach out to you via call or WhatsApp shortly.
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEnquirySuccess(false)}
                      className="text-xs uppercase font-bold mt-2"
                    >
                      Submit Another Query
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={handleEnquirySubmit} className="space-y-4">
                    {enquiryError && (
                      <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-500 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 shrink-0" />
                        {enquiryError}
                      </div>
                    )}

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Full Name *</label>
                        <Input
                          placeholder="e.g. John Doe"
                          value={enquiryForm.name}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, name: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Mobile Number (WhatsApp) *</label>
                        <Input
                          placeholder="+91 98765 43210"
                          value={enquiryForm.phone}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, phone: e.target.value })}
                          required
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Email Address (Optional)</label>
                        <Input
                          type="email"
                          placeholder="john@example.com"
                          value={enquiryForm.email}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, email: e.target.value })}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Preferred Gym Branch</label>
                        <Select
                          value={enquiryForm.preferred_branch_id}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, preferred_branch_id: e.target.value })}
                        >
                          <option value="">Select Location (Any Branch)</option>
                          {branches?.map((b) => (
                            <option key={b.id} value={String(b.id)}>
                              {b.name} ({b.city})
                            </option>
                          ))}
                        </Select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Primary Fitness Goal</label>
                        <Select
                          value={enquiryForm.fitness_goal}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, fitness_goal: e.target.value })}
                        >
                          <option value="muscle_building">Hypertrophy & Muscle Building</option>
                          <option value="fat_loss">Fat Loss & Body Conditioning</option>
                          <option value="strength_powerlifting">Strength & Olympic Powerlifting</option>
                          <option value="endurance">Stamina & Athletic Endurance</option>
                          <option value="general_fitness">General Health & Mobility</option>
                        </Select>
                      </div>
                      <div>
                        <label className="block text-xs font-bold text-slate-700 dark:text-zinc-300 mb-1">Preferred Time / Questions</label>
                        <Input
                          placeholder="e.g. Morning 7 AM, interested in personal coach"
                          value={enquiryForm.notes}
                          onChange={(e) => setEnquiryForm({ ...enquiryForm, notes: e.target.value })}
                        />
                      </div>
                    </div>

                    <Button
                      type="submit"
                      variant="primary"
                      size="lg"
                      disabled={createEnquiryMutation.isPending}
                      className="w-full text-xs uppercase font-black tracking-wider shadow-lg mt-2"
                    >
                      {createEnquiryMutation.isPending ? 'Sending Request...' : 'Book Free Assessment Now'}
                      <Send className="w-4 h-4 ml-2" />
                    </Button>
                  </form>
                )}
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* 8. LOCATIONS */}
      <section id="branches" className="py-24 px-4 sm:px-8 bg-slate-50 dark:bg-[#040406] border-t border-slate-200 dark:border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <Badge variant="rage">Facility Network</Badge>
            <h2 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight uppercase">
              Our Gym Branch Locations
            </h2>
            <p className="text-xs uppercase tracking-widest text-slate-500 dark:text-zinc-400">
              Metropolitan locations equipped with complete lifting and recovery amenities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {branches?.map((b) => (
              <Card key={b.id} className="p-7">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-black text-slate-900 dark:text-white uppercase">{b.name}</h3>
                    <span className="text-xs font-mono font-bold text-slate-500 dark:text-zinc-400">{b.code}</span>
                  </div>
                  <Badge variant="success">Open 24/7</Badge>
                </div>
                <div className="space-y-2 text-xs text-slate-600 dark:text-zinc-300 border-t border-slate-100 dark:border-white/10 pt-3">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{b.address}, {b.city}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{b.phone}</span>
                  </div>
                  {b.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4 text-slate-400 shrink-0" />
                      <span>{b.email}</span>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* 8. FOOTER */}
      <footer className="bg-slate-900 dark:bg-[#030305] text-slate-400 border-t border-slate-800 dark:border-white/10 py-12 px-4 sm:px-8 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white text-black flex items-center justify-center font-black">
              <Flame className="w-5 h-5 text-black" />
            </div>
            <div>
              <span className="font-black text-white text-sm tracking-wider">SETFIT ELITE FITNESS</span>
              <p className="text-[11px] text-slate-400">
                © 2026 {settings?.gym_name || 'SETFIT'} Inc. All rights reserved. • {settings?.contact_phone || '+91 98765 43210'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 uppercase tracking-wider text-[11px] font-bold">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#plans" className="hover:text-white transition-colors">Plans (₹)</a>
            <a href="#trainers" className="hover:text-white transition-colors">Trainers</a>
            <button
              onClick={() => onNavigateAdminControl && onNavigateAdminControl()}
              className="text-slate-600 hover:text-slate-400 transition-colors cursor-pointer text-[10px]"
              title="Restricted Staff Portal"
            >
              Control Portal
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
