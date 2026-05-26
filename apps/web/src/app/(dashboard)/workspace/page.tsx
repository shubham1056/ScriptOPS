'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { MessageSquarePlus, Sparkles } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

import { ChatComposer } from '@/components/chat/chat-composer';
import { ChatMessage } from '@/components/chat/chat-message';
import { ExportMenu } from '@/components/export-menu';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { conversationsApi } from '@/lib/api/endpoints';
import { API_BASE_URL, API_PREFIX, APP_TAGLINE, STORAGE_KEYS } from '@/lib/constants';

interface LocalMsg {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  streaming?: boolean;
}

export default function WorkspacePage() {
  const qc = useQueryClient();
  const [activeId, setActiveId] = useState<string | null>(null);
  const [localMsgs, setLocalMsgs] = useState<LocalMsg[]>([]);
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: conversationsApi.list,
  });

  const { data: current } = useQuery({
    queryKey: ['conversation', activeId],
    queryFn: () => conversationsApi.get(activeId!),
    enabled: !!activeId,
  });

  useEffect(() => {
    if (current) {
      setLocalMsgs(
        current.messages.map((m) => ({
          id: m.id,
          role: m.role === 'user' ? 'user' : 'assistant',
          content: m.content,
        })),
      );
    }
  }, [current]);

  const createConv = useMutation({
    mutationFn: () => conversationsApi.create(),
    onSuccess: (c) => {
      qc.invalidateQueries({ queryKey: ['conversations'] });
      setActiveId(c.id);
      setLocalMsgs([]);
    },
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [localMsgs]);

  const handleSend = async (text: string) => {
    let convId = activeId;
    if (!convId) {
      const conv = await conversationsApi.create();
      convId = conv.id;
      setActiveId(convId);
      qc.invalidateQueries({ queryKey: ['conversations'] });
    }

    const userMsg: LocalMsg = { id: crypto.randomUUID(), role: 'user', content: text };
    const aiMsg: LocalMsg = { id: crypto.randomUUID(), role: 'assistant', content: '', streaming: true };
    setLocalMsgs((p) => [...p, userMsg, aiMsg]);
    setSending(true);

    try {
      const token =
        typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEYS.accessToken) : null;
      const res = await fetch(
        `${API_BASE_URL}${API_PREFIX}/conversations/${convId}/messages/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ content: text }),
        },
      );
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
            const { token: tok } = JSON.parse(dataLine.slice(5).trim());
            if (tok) {
              setLocalMsgs((prev) =>
                prev.map((m) => (m.id === aiMsg.id ? { ...m, content: m.content + tok } : m)),
              );
            }
          } catch {}
        }
      }
    } catch {
      toast.error('Stream failed');
    } finally {
      setLocalMsgs((prev) =>
        prev.map((m) => (m.id === aiMsg.id ? { ...m, streaming: false } : m)),
      );
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Conversation list */}
      <div className="hidden md:flex w-72 flex-col border-r border-ivory-300 bg-ivory-100/40">
        <div className="p-4">
          <Button className="w-full" onClick={() => createConv.mutate()}>
            <MessageSquarePlus className="h-4 w-4" /> New conversation
          </Button>
        </div>
        <ScrollArea className="flex-1 px-2">
          {isLoading ? (
            <div className="space-y-2 px-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            (conversations ?? []).map((c) => (
              <button
                key={c.id}
                onClick={() => setActiveId(c.id)}
                className={`w-full text-left rounded-md px-3 py-2 text-sm transition ${
                  activeId === c.id ? 'bg-ivory-200 text-ink-900' : 'text-ink-700 hover:bg-ivory-200/60'
                }`}
              >
                <div className="truncate">{c.title}</div>
              </button>
            ))
          )}
        </ScrollArea>
      </div>

      {/* Chat panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {activeId && current && (
          <div className="flex items-center justify-between gap-3 border-b border-ivory-300 bg-ivory-50/60 px-6 py-2">
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-ink-800">{current.title}</div>
              <div className="text-[11px] text-ink-500">
                {current.messages.length} message{current.messages.length === 1 ? '' : 's'}
                {current.sop_id ? ' · linked SOP' : ''}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {current.sop_id && (
                <ExportMenu
                  endpoint={`/sops/${current.sop_id}/download`}
                  filenameHint={current.title || 'sop'}
                  label="Download SOP"
                  variant="secondary"
                  size="sm"
                />
              )}
              <ExportMenu
                endpoint={`/conversations/${current.id}/download`}
                filenameHint={current.title || 'conversation'}
                label="Download chat"
                variant={current.sop_id ? 'outline' : 'secondary'}
                size="sm"
                disabled={current.messages.length === 0}
              />
            </div>
          </div>
        )}
        <div ref={scrollRef} className="flex-1 overflow-auto">
          <div className="max-w-3xl mx-auto px-6 py-8">
            {localMsgs.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-20"
              >
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-50 border border-accent-100 text-accent-700 text-xs font-medium mb-4">
                  <Sparkles className="h-3.5 w-3.5" /> GPT-5 · Streaming
                </div>
                <h1 className="font-serif text-4xl text-ink-900">What shall we draft?</h1>
                <p className="text-ink-600 mt-2">{APP_TAGLINE}</p>
              </motion.div>
            ) : (
              <div className="space-y-1">
                {localMsgs.map((m) => (
                  <ChatMessage key={m.id} role={m.role} content={m.content} streaming={m.streaming} />
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-ivory-300 bg-ivory-50/70 backdrop-blur p-4">
          <div className="max-w-3xl mx-auto">
            <ChatComposer onSend={handleSend} disabled={sending} />
            <p className="text-[11px] text-ink-500 text-center mt-2">
              TranscribeOP can make mistakes. Verify generated SOPs before publishing.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
