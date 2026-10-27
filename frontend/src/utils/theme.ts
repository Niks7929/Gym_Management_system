export type ThemeAccent = 'crimson' | 'cyan' | 'emerald' | 'gold' | 'violet' | 'orange';

export interface ThemeConfig {
  id: ThemeAccent;
  name: string;
  primaryColor: string;
  glowColor: string;
  badgeBg: string;
  badgeBorder: string;
  badgeText: string;
  gradientFrom: string;
  gradientTo: string;
  buttonClass: string;
  textAccentClass: string;
  borderAccentClass: string;
  shadowGlowClass: string;
}

export const THEME_CONFIGS: Record<ThemeAccent, ThemeConfig> = {
  crimson: {
    id: 'crimson',
    name: 'Dark Rage Crimson',
    primaryColor: '#ef4444',
    glowColor: 'rgba(239, 68, 68, 0.45)',
    badgeBg: 'bg-red-950/80',
    badgeBorder: 'border-red-800/60',
    badgeText: 'text-red-400',
    gradientFrom: 'from-red-600',
    gradientTo: 'to-rose-950',
    buttonClass: 'bg-red-600 hover:bg-red-700 text-white shadow-red-500/30',
    textAccentClass: 'text-red-500',
    borderAccentClass: 'border-red-600',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(239,68,68,0.4)]',
  },
  cyan: {
    id: 'cyan',
    name: 'Cyber Electric Cyan',
    primaryColor: '#06b6d4',
    glowColor: 'rgba(6, 182, 212, 0.45)',
    badgeBg: 'bg-cyan-950/80',
    badgeBorder: 'border-cyan-800/60',
    badgeText: 'text-cyan-400',
    gradientFrom: 'from-cyan-500',
    gradientTo: 'to-blue-950',
    buttonClass: 'bg-cyan-600 hover:bg-cyan-700 text-white shadow-cyan-500/30',
    textAccentClass: 'text-cyan-400',
    borderAccentClass: 'border-cyan-500',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(6,182,212,0.4)]',
  },
  emerald: {
    id: 'emerald',
    name: 'Bio-Mech Toxic Emerald',
    primaryColor: '#10b981',
    glowColor: 'rgba(16, 185, 129, 0.45)',
    badgeBg: 'bg-emerald-950/80',
    badgeBorder: 'border-emerald-800/60',
    badgeText: 'text-emerald-400',
    gradientFrom: 'from-emerald-500',
    gradientTo: 'to-teal-950',
    buttonClass: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-500/30',
    textAccentClass: 'text-emerald-400',
    borderAccentClass: 'border-emerald-500',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(16,185,129,0.4)]',
  },
  gold: {
    id: 'gold',
    name: 'Olympian Royal Gold',
    primaryColor: '#f59e0b',
    glowColor: 'rgba(245, 158, 11, 0.45)',
    badgeBg: 'bg-amber-950/80',
    badgeBorder: 'border-amber-800/60',
    badgeText: 'text-amber-400',
    gradientFrom: 'from-amber-500',
    gradientTo: 'to-yellow-950',
    buttonClass: 'bg-amber-600 hover:bg-amber-700 text-black font-black shadow-amber-500/30',
    textAccentClass: 'text-amber-400',
    borderAccentClass: 'border-amber-500',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(245,158,11,0.4)]',
  },
  violet: {
    id: 'violet',
    name: 'Neon Cyber Violet',
    primaryColor: '#8b5cf6',
    glowColor: 'rgba(139, 92, 246, 0.45)',
    badgeBg: 'bg-purple-950/80',
    badgeBorder: 'border-purple-800/60',
    badgeText: 'text-purple-400',
    gradientFrom: 'from-purple-600',
    gradientTo: 'to-indigo-950',
    buttonClass: 'bg-purple-600 hover:bg-purple-700 text-white shadow-purple-500/30',
    textAccentClass: 'text-purple-400',
    borderAccentClass: 'border-purple-500',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(139,92,246,0.4)]',
  },
  orange: {
    id: 'orange',
    name: 'Inferno Forge Orange',
    primaryColor: '#f97316',
    glowColor: 'rgba(249, 115, 22, 0.45)',
    badgeBg: 'bg-orange-950/80',
    badgeBorder: 'border-orange-800/60',
    badgeText: 'text-orange-400',
    gradientFrom: 'from-orange-500',
    gradientTo: 'to-red-950',
    buttonClass: 'bg-orange-600 hover:bg-orange-700 text-white shadow-orange-500/30',
    textAccentClass: 'text-orange-400',
    borderAccentClass: 'border-orange-500',
    shadowGlowClass: 'shadow-[0_0_25px_-5px_rgba(249,115,22,0.4)]',
  },
};

export function getThemeConfig(accentName?: string): ThemeConfig {
  const key = (accentName?.toLowerCase() || 'crimson') as ThemeAccent;
  return THEME_CONFIGS[key] || THEME_CONFIGS.crimson;
}

export function applyThemeVariables(accentName?: string) {
  const theme = getThemeConfig(accentName);
  if (typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--brand-primary', theme.primaryColor);
    document.documentElement.style.setProperty('--brand-glow', theme.glowColor);
  }
}
