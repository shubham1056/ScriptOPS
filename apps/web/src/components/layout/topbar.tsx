'use client';

import { LogOut, Search } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ROUTES } from '@/lib/constants';
import { initials } from '@/lib/utils';
import { useAuthStore } from '@/stores/auth-store';

export function Topbar() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const onLogout = () => {
    logout();
    router.replace(ROUTES.login);
  };

  return (
    <header className="h-16 border-b border-ivory-300 bg-ivory-50/80 backdrop-blur-md flex items-center justify-between px-6">
      <div className="relative max-w-md w-full">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-400" />
        <input
          placeholder="Search SOPs, transcripts, conversations..."
          className="w-full pl-10 pr-3 py-2 rounded-md bg-ivory-100 border border-transparent hover:border-ivory-300 focus:border-accent-300 focus:bg-white focus:outline-none focus:ring-2 focus:ring-ring text-sm transition"
        />
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right hidden md:block">
          <div className="text-sm font-medium text-ink-900">{user?.full_name ?? 'Guest'}</div>
          <div className="text-xs text-ink-500">{user?.email}</div>
        </div>
        <Avatar>
          <AvatarFallback>{user ? initials(user.full_name) : 'G'}</AvatarFallback>
        </Avatar>
        <Button variant="ghost" size="icon" onClick={onLogout} aria-label="Logout">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
