'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Loader2, RefreshCw } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

import { ExportMenu } from '@/components/export-menu';
import { MarkdownView } from '@/components/sop/markdown-view';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { sopsApi } from '@/lib/api/endpoints';
import { API_BASE_URL, API_PREFIX, STORAGE_KEYS } from '@/lib/constants';
import { formatDate } from '@/lib/utils';

export default function SopPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const [refinement, setRefinement] = useState('');
  const [streaming, setStreaming] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const { data: sop, refetch } = useQuery({
    queryKey: ['sop', id],
    queryFn: () => sopsApi.get(id),
    refetchInterval: (q) =>
      q.state.data?.status === 'QUEUED' || q.state.data?.status === 'GENERATING' ? 2000 : false,
  });

  // SSE refinement
  const refine = async () => {
    if (!refinement.trim() || !sop) return;
    setIsStreaming(true);
    setStreaming('');
    const token =
      typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEYS.accessToken) : null;
    const url = `${API_BASE_URL}${API_PREFIX}/sops/${id}/stream?message=${encodeURIComponent(refinement)}`;

    try {
      const res = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (!res.body) throw new Error('No stream');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() ?? '';
        for (const evt of events) {
          if (evt.startsWith('event: done')) continue;
          const dataLine = evt.split('\n').find((l) => l.startsWith('data:'));
          if (!dataLine) continue;
          try {
            const parsed = JSON.parse(dataLine.slice(5).trim());
            if (parsed.token) setStreaming((s) => s + parsed.token);
          } catch {}
        }
      }
      // Save refined SOP
      await sopsApi.update(id, { markdown: (sop.markdown ?? '') + '\n\n---\n\n' + streaming });
      qc.invalidateQueries({ queryKey: ['sop', id] });
      toast.success('SOP refined');
    } catch (e: any) {
      toast.error('Streaming failed');
    } finally {
      setIsStreaming(false);
      setRefinement('');
    }
  };

  useEffect(() => {
    if (sop?.status === 'COMPLETED') void refetch();
  }, [sop?.status, refetch]);

  if (!sop) {
    return (
      <div className="p-6 lg:p-10 max-w-5xl mx-auto space-y-4">
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  const statusVariant =
    sop.status === 'COMPLETED' ? 'success' : sop.status === 'FAILED' ? 'danger' : 'warning';

  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4"
      >
        <div>
          <Badge variant={statusVariant} className="mb-2">
            {sop.status}
          </Badge>
          <h1 className="font-serif text-3xl text-ink-900">{sop.title}</h1>
          <p className="text-ink-500 text-sm mt-1">
            Updated {formatDate(sop.updated_at)} · {sop.tokens_used.toLocaleString()} tokens
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" /> Refresh
          </Button>
          <ExportMenu
            endpoint={`/sops/${sop.id}/download`}
            filenameHint={sop.title}
            disabled={!sop.markdown}
          />
        </div>
      </motion.div>

      <Card>
        <CardContent className="p-8">
          {sop.status === 'COMPLETED' && sop.markdown ? (
            <MarkdownView markdown={sop.markdown} />
          ) : sop.status === 'FAILED' ? (
            <div className="text-destructive">
              <strong>Generation failed:</strong> {sop.error_message}
            </div>
          ) : (
            <div className="flex items-center gap-3 text-ink-600">
              <Loader2 className="h-4 w-4 animate-spin text-accent-500" />
              GPT-5 is structuring your SOP…
            </div>
          )}
        </CardContent>
      </Card>

      {sop.status === 'COMPLETED' && (
        <Card>
          <CardContent className="p-6 space-y-3">
            <h3 className="font-serif text-lg">Refine with AI</h3>
            <Textarea
              placeholder="e.g. Add a rollback section, tighten the validation steps, target SRE audience."
              value={refinement}
              onChange={(e) => setRefinement(e.target.value)}
            />
            {isStreaming && streaming && (
              <div className="rounded-md border border-ivory-300 bg-ivory-50 p-4">
                <MarkdownView markdown={streaming} />
              </div>
            )}
            <Button onClick={refine} disabled={isStreaming || !refinement.trim()}>
              {isStreaming && <Loader2 className="h-4 w-4 animate-spin" />}
              Stream refinement
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
