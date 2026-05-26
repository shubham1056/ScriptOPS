'use client';

import { useQuery } from '@tanstack/react-query';
import { FileText, Sparkles } from 'lucide-react';
import Link from 'next/link';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { sopsApi } from '@/lib/api/endpoints';
import { ROUTES } from '@/lib/constants';
import { formatDate } from '@/lib/utils';

export default function HistoryPage() {
  const { data: sops, isLoading } = useQuery({ queryKey: ['sops'], queryFn: sopsApi.list });

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto space-y-6">
      <div>
        <Badge variant="accent" className="mb-2">
          <Sparkles className="h-3 w-3 mr-1" /> Archive
        </Badge>
        <h1 className="font-serif text-3xl text-ink-900">SOP History</h1>
        <p className="text-ink-600 mt-1">All Standard Operating Procedures you've generated.</p>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-36 w-full" />
          ))}
        </div>
      ) : sops && sops.length > 0 ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sops.map((sop) => (
            <Link key={sop.id} href={ROUTES.sop(sop.id)}>
              <Card className="h-full hover:shadow-lift transition-shadow group">
                <CardContent className="p-5 flex flex-col gap-3 h-full">
                  <div className="h-9 w-9 rounded-lg bg-ivory-100 border border-ivory-300 grid place-items-center text-ink-600 group-hover:bg-accent-50 group-hover:border-accent-200 group-hover:text-accent-600 transition">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-serif text-lg text-ink-900 line-clamp-2">{sop.title}</h3>
                    <p className="text-xs text-ink-500 mt-1">{formatDate(sop.updated_at)}</p>
                  </div>
                  <Badge
                    variant={
                      sop.status === 'COMPLETED'
                        ? 'success'
                        : sop.status === 'FAILED'
                          ? 'danger'
                          : 'warning'
                    }
                    className="w-fit"
                  >
                    {sop.status}
                  </Badge>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-16 text-center">
            <p className="text-ink-600">No SOPs generated yet.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
