import React, { type ReactNode } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Button ---
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'rage' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    const variants = {
      primary:
        'bg-slate-900 text-white hover:bg-black dark:bg-white dark:text-black dark:hover:bg-zinc-200 font-extrabold shadow-black-btn dark:shadow-white-btn active:scale-[0.98]',
      rage:
        'bg-slate-900 text-white hover:bg-black dark:bg-white dark:text-black dark:hover:bg-zinc-200 font-extrabold shadow-black-btn dark:shadow-white-btn active:scale-[0.98]',
      secondary:
        'bg-slate-100 hover:bg-slate-200 text-slate-900 border border-slate-200 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:text-zinc-100 dark:border-zinc-800 active:scale-[0.98]',
      outline:
        'bg-transparent border border-slate-300 text-slate-800 hover:bg-slate-100 dark:border-white/20 dark:text-white dark:hover:bg-white/10 active:scale-[0.98]',
      ghost:
        'bg-transparent hover:bg-slate-100 text-slate-700 hover:text-black dark:hover:bg-zinc-800 dark:text-zinc-300 dark:hover:text-white',
      danger:
        'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 dark:bg-zinc-900 dark:hover:bg-red-950/60 dark:text-red-400 dark:border-red-900/60',
    };

    const sizes = {
      sm: 'px-3.5 py-1.5 text-xs rounded-xl',
      md: 'px-5 py-2.5 text-sm rounded-xl',
      lg: 'px-7 py-3.5 text-base rounded-2xl font-black',
    };

    return (
      <button
        ref={ref}
        disabled={isLoading || disabled}
        className={cn(
          'inline-flex items-center justify-center gap-2 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer tracking-wide',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

// --- Card ---
export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200 dark:bg-[#0b0b0f] dark:border-white/10 rounded-2xl p-6 shadow-clean-card transition-all duration-200',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('flex flex-col space-y-1.5 mb-4', className)} {...props}>{children}</div>;
}

export function CardTitle({ className, children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cn('text-lg font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2', className)} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className, children, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('text-xs text-slate-500 dark:text-zinc-400', className)} {...props}>{children}</p>;
}

export function CardContent({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('', className)} {...props}>{children}</div>;
}

// --- Badge ---
export function Badge({
  children,
  variant = 'default',
  className
}: {
  children: ReactNode;
  variant?: 'default' | 'white' | 'success' | 'warning' | 'danger' | 'rage' | 'outline' | 'purple';
  className?: string;
}) {
  const variants = {
    default: 'bg-slate-100 text-slate-800 border-slate-200 dark:bg-zinc-800/80 dark:text-zinc-200 dark:border-zinc-700',
    white: 'bg-slate-900 text-white dark:bg-white dark:text-black font-black border-transparent shadow-sm',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-zinc-900 dark:text-emerald-300 dark:border-emerald-800/50',
    warning: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-zinc-900 dark:text-amber-300 dark:border-amber-800/50',
    danger: 'bg-red-50 text-red-700 border-red-200 dark:bg-zinc-900 dark:text-red-400 dark:border-red-800/50',
    rage: 'bg-slate-900 text-white dark:bg-zinc-900 dark:text-white dark:border-white/20 font-bold',
    purple: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-zinc-900 dark:text-zinc-200 dark:border-zinc-700',
    outline: 'bg-transparent text-slate-700 border-slate-300 dark:text-zinc-300 dark:border-white/15',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

// --- StatCard ---
export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: any;
  trend?: string;
  [key: string]: any;
}) {
  return (
    <Card className="relative overflow-hidden border border-slate-200 dark:border-white/10 hover:shadow-md dark:hover:border-white/25 transition-all duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 mb-1">{title}</p>
          <h2 className="text-2xl lg:text-3xl font-black text-slate-900 dark:text-white tracking-tight font-mono">{value}</h2>
          {subtitle && <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">{subtitle}</p>}
          {trend && <span className="inline-block text-xs text-emerald-600 dark:text-zinc-300 font-semibold mt-2">{trend}</span>}
        </div>
        {Icon && (
          <div className="p-3 rounded-2xl bg-slate-100 text-slate-900 dark:bg-zinc-900 dark:border dark:border-white/10 dark:text-white">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </Card>
  );
}

// --- Modal Dialog ---
export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  maxWidth = 'max-w-xl'
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  maxWidth?: string;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className={cn(
          'w-full bg-white dark:bg-[#0d0d12] border border-slate-200 dark:border-white/15 rounded-3xl shadow-2xl p-6 sm:p-8 relative max-h-[90vh] overflow-y-auto',
          maxWidth
        )}
      >
        <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-zinc-800 mb-5">
          <div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white tracking-tight">{title}</h3>
            {description && <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
          >
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// --- Input & Form components ---
export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 dark:bg-[#07070a] dark:border-zinc-800 rounded-xl text-sm text-slate-900 dark:text-zinc-100 placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:border-slate-900 dark:focus:border-white focus:ring-1 focus:ring-slate-900 dark:focus:ring-white transition-all',
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        ref={ref}
        className={cn(
          'w-full px-4 py-2.5 bg-slate-50 border border-slate-200 dark:bg-[#07070a] dark:border-zinc-800 rounded-xl text-sm text-slate-900 dark:text-zinc-100 focus:outline-none focus:border-slate-900 dark:focus:border-white focus:ring-1 focus:ring-slate-900 dark:focus:ring-white transition-all cursor-pointer',
          className
        )}
        {...props}
      >
        {children}
      </select>
    );
  }
);
Select.displayName = 'Select';
