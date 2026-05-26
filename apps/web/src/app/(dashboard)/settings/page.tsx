'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { APP_NAME, APP_TAGLINE } from '@/lib/constants';
import { useAuthStore } from '@/stores/auth-store';

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto space-y-6">
      <div>
        <Badge variant="accent" className="mb-2">Account</Badge>
        <h1 className="font-serif text-3xl text-ink-900">Settings</h1>
        <p className="text-ink-600 mt-1">Manage your profile and platform preferences.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Row label="Name" value={user?.full_name ?? '—'} />
          <Separator />
          <Row label="Email" value={user?.email ?? '—'} />
          <Separator />
          <Row label="Role" value={user?.role ?? '—'} />
          <Separator />
          <Row label="Account ID" value={user?.id ?? '—'} mono />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-ink-600">
          <div>
            <span className="text-ink-900 font-medium">{APP_NAME}</span> — {APP_TAGLINE}
          </div>
          <div>Powered by Azure OpenAI GPT-5.</div>
          <div className="text-xs text-ink-500">v1.0.0 · © 2026 TranscribeOP</div>
        </CardContent>
      </Card>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-ink-500">{label}</span>
      <span className={`text-sm text-ink-900 ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
    </div>
  );
}
