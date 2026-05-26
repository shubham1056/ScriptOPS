'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowUpRight, FileText, MessageSquareText, Sparkles, Upload } from 'lucide-react';
import Link from 'next/link';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { documentsApi, sopsApi } from '@/lib/api/endpoints';
import { ROUTES } from '@/lib/constants';
import { formatDate } from '@/lib/utils';
import { useAuthStore } from '@/stores/auth-store';

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const { data: sops, isLoading: loadingSops } = useQuery({
    queryKey: ['sops'],
    queryFn: sopsApi.list,
  });
  const { data: docs, isLoading: loadingDocs } = useQuery({
    queryKey: ['documents'],
    queryFn: documentsApi.list,
  });

  const stats = [
    { label: 'SOPs Generated', value: sops?.length ?? 0, icon: FileText },
    { label: 'Documents Uploaded', value: docs?.length ?? 0, icon: Upload },
    { label: 'GPT-5 Model', value: 'Active', icon: Sparkles },
  ];

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4"
      >
        <div>
          <Badge variant="accent" className="mb-2">
            <Sparkles className="h-3 w-3 mr-1" /> Welcome
          </Badge>
          <h1 className="font-serif text-3xl lg:text-4xl text-ink-900">
            Hello, <em className="text-accent-600 not-italic">{user?.full_name.split(' ')[0]}</em>.
          </h1>
          <p className="text-ink-600 mt-1">
            What knowledge will you turn into an SOP today?
          </p>
        </div>

        <div className="flex gap-2">
          <Button asChild variant="secondary">
            <Link href={ROUTES.upload}>
              <Upload className="h-4 w-4" /> Upload
            </Link>
          </Button>
          <Button asChild>
            <Link href={ROUTES.workspace}>
              <MessageSquareText className="h-4 w-4" /> Open Workspace
            </Link>
          </Button>
        </div>
      </motion.div>

      <div className="grid sm:grid-cols-3 gap-4">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card>
              <CardContent className="p-5 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wider text-ink-500">{s.label}</p>
                  <p className="font-serif text-3xl text-ink-900 mt-1">{s.value}</p>
                </div>
                <div className="h-11 w-11 rounded-lg bg-accent-50 border border-accent-100 grid place-items-center text-accent-600">
                  <s.icon className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent SOPs</CardTitle>
          <Button asChild variant="ghost" size="sm">
            <Link href={ROUTES.history}>
              View all <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent className="space-y-1">
          {loadingSops ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          ) : sops && sops.length > 0 ? (
            sops.slice(0, 6).map((sop) => (
              <Link
                key={sop.id}
                href={ROUTES.sop(sop.id)}
                className="flex items-center justify-between rounded-md px-3 py-3 hover:bg-ivory-100 transition-colors group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="h-9 w-9 rounded-md bg-ivory-100 border border-ivory-300 grid place-items-center">
                    <FileText className="h-4 w-4 text-ink-600" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-ink-900 truncate">{sop.title}</div>
                    <div className="text-xs text-ink-500">{formatDate(sop.updated_at)}</div>
                  </div>
                </div>
                <Badge
                  variant={
                    sop.status === 'COMPLETED'
                      ? 'success'
                      : sop.status === 'FAILED'
                        ? 'danger'
                        : 'warning'
                  }
                >
                  {sop.status}
                </Badge>
              </Link>
            ))
          ) : (
            <div className="py-10 text-center">
              <p className="text-ink-600">No SOPs yet.</p>
              <Button asChild className="mt-3">
                <Link href={ROUTES.upload}>Upload your first transcript</Link>
              </Button>
            </div>
          )}
          {loadingDocs && null}
        </CardContent>
      </Card>
    </div>
  );
}
