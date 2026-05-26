'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { toast } from 'sonner';

import { Dropzone, type UploadFileItem } from '@/components/upload/dropzone';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { documentsApi, sopsApi } from '@/lib/api/endpoints';
import { ROUTES } from '@/lib/constants';
import { formatBytes } from '@/lib/utils';

export default function UploadPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [items, setItems] = useState<UploadFileItem[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [instructions, setInstructions] = useState('');

  const { data: documents } = useQuery({ queryKey: ['documents'], queryFn: documentsApi.list });

  const upload = useMutation({
    mutationFn: async (file: File) => documentsApi.upload(file),
    onSuccess: (doc) => {
      qc.invalidateQueries({ queryKey: ['documents'] });
      setSelectedDoc(doc.id);
      toast.success(`Uploaded ${doc.filename}`);
    },
  });

  const generate = useMutation({
    mutationFn: () => sopsApi.generate(selectedDoc!, title || undefined, instructions || undefined),
    onSuccess: (sop) => {
      toast.success('SOP generation started');
      qc.invalidateQueries({ queryKey: ['sops'] });
      router.push(ROUTES.sop(sop.id));
    },
    onError: (e: any) => toast.error(e?.response?.data?.error?.message ?? 'Failed to start generation'),
  });

  const onFiles = async (files: File[]) => {
    const newItems: UploadFileItem[] = files.map((f) => ({
      id: `${f.name}-${Date.now()}-${Math.random()}`,
      file: f,
      progress: 0,
      status: 'uploading',
    }));
    setItems((prev) => [...prev, ...newItems]);

    for (const it of newItems) {
      try {
        const doc = await documentsApi.upload(it.file, (pct) =>
          setItems((prev) => prev.map((p) => (p.id === it.id ? { ...p, progress: pct } : p))),
        );
        setItems((prev) =>
          prev.map((p) => (p.id === it.id ? { ...p, progress: 100, status: 'done' } : p)),
        );
        setSelectedDoc(doc.id);
        qc.invalidateQueries({ queryKey: ['documents'] });
      } catch (err: any) {
        setItems((prev) =>
          prev.map((p) =>
            p.id === it.id
              ? { ...p, status: 'error', error: err?.response?.data?.error?.message ?? 'Upload failed' }
              : p,
          ),
        );
      }
    }
  };

  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto space-y-8">
      <div>
        <Badge variant="accent" className="mb-2">
          <Sparkles className="h-3 w-3 mr-1" /> Step 1 — Upload
        </Badge>
        <h1 className="font-serif text-3xl text-ink-900">Upload Center</h1>
        <p className="text-ink-600 mt-1">
          Upload transcripts, KT recordings, or operational documents. We extract the text,
          chunk it for GPT-5, then generate a structured SOP.
        </p>
      </div>

      <Dropzone
        items={items}
        onFiles={onFiles}
        onRemove={(id) => setItems((prev) => prev.filter((i) => i.id !== id))}
      />

      <Card>
        <CardHeader>
          <CardTitle>Select source & generate SOP</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-medium text-ink-700 uppercase tracking-wider">
              Source document
            </label>
            <div className="grid sm:grid-cols-2 gap-2 max-h-64 overflow-auto pr-1">
              {(documents ?? []).map((d) => (
                <button
                  key={d.id}
                  onClick={() => setSelectedDoc(d.id)}
                  className={`text-left rounded-md border px-3 py-2.5 transition ${
                    selectedDoc === d.id
                      ? 'border-accent-500 bg-accent-50/60 ring-1 ring-accent-300'
                      : 'border-ivory-300 hover:bg-ivory-100'
                  }`}
                >
                  <div className="text-sm font-medium text-ink-900 truncate">{d.filename}</div>
                  <div className="text-xs text-ink-500">
                    {d.extension.toUpperCase()} · {formatBytes(d.size_bytes)}
                  </div>
                </button>
              ))}
              {(!documents || documents.length === 0) && (
                <div className="col-span-full text-sm text-ink-500 text-center py-8">
                  Upload a file above to begin.
                </div>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-ink-700 uppercase tracking-wider">
              SOP title (optional)
            </label>
            <Input
              placeholder="e.g. Production Deployment Runbook"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-medium text-ink-700 uppercase tracking-wider">
              Custom instructions (optional)
            </label>
            <Textarea
              placeholder="e.g. Focus on rollback procedures and emphasize SRE handoff."
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              rows={4}
            />
          </div>

          <Button
            size="lg"
            className="w-full"
            disabled={!selectedDoc || generate.isPending}
            onClick={() => generate.mutate()}
          >
            {generate.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            Generate SOP with GPT-5
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
