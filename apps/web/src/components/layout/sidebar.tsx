'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  MessageSquareText,
  Upload,
  History,
  Settings,
  Sparkles,
} from 'lucide-react';

import { BrandMark } from '@/components/layout/brand';
import { ROUTES } from '@/lib/constants';
import { cn } from '@/lib/utils';

const NAV = [
  { href: ROUTES.dashboard, label: 'Dashboard', icon: LayoutDashboard },
  { href: ROUTES.workspace, label: 'Workspace', icon: MessageSquareText },
  { href: ROUTES.upload, label: 'Upload Center', icon: Upload },
  { href: ROUTES.history, label: 'SOP History', icon: History },
  { href: ROUTES.settings, label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-ivory-300 bg-ivory-100/60 backdrop-blur-sm">
      <div className="p-5">
        <BrandMark />
      </div>

      <nav className="flex-1 px-3 space-y-0.5">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = pathname?.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'relative flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                active
                  ? 'text-ink-900 bg-ivory-200'
                  : 'text-ink-600 hover:text-ink-900 hover:bg-ivory-200/60',
              )}
            >
              {active && (
                <motion.span
                  layoutId="sidebar-active"
                  className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-r bg-accent-500"
                />
              )}
              <Icon className="h-4 w-4" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 m-3 rounded-lg bg-gradient-to-br from-accent-50 to-ivory-100 border border-accent-100">
        <div className="flex items-center gap-2 text-accent-700 text-xs font-medium">
          <Sparkles className="h-3.5 w-3.5" />
          POWERED BY GPT-5
        </div>
        <p className="mt-1.5 text-xs text-ink-600 leading-relaxed">
          Generate audit-ready SOPs from transcripts in seconds.
        </p>
      </div>
    </aside>
  );
}
