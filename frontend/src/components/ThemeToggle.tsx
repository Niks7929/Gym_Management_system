import React from 'react';
import { useThemeStore } from '../contexts/themeStore';
import { Sun, Moon } from 'lucide-react';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, toggleTheme } = useThemeStore();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      type="button"
      className={`p-2 rounded-xl border transition-all duration-200 cursor-pointer flex items-center justify-center ${
        isDark
          ? 'bg-zinc-900 border-white/15 text-yellow-400 hover:text-white hover:bg-zinc-800'
          : 'bg-white border-slate-200 text-slate-700 hover:text-black hover:bg-slate-100 shadow-sm'
      } ${className}`}
      title={isDark ? 'Switch to Clean Light Theme' : 'Switch to Dark Rage Theme'}
      aria-label="Toggle Theme"
    >
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </button>
  );
};
