'use client';

import { motion } from 'framer-motion';
import { Bot, User as UserIcon } from 'lucide-react';

import { MarkdownView } from '@/components/sop/markdown-view';
import { cn } from '@/lib/utils';

interface Props {
  role: 'user' | 'assistant';
  content: string;
  streaming?: boolean;
}

export function ChatMessage({ role, content, streaming }: Props) {
  const isUser = role === 'user';
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-4 py-4', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      <div
        className={cn(
          'h-8 w-8 shrink-0 rounded-lg grid place-items-center text-white',
          isUser ? 'bg-ink-800' : 'bg-gradient-to-br from-accent-500 to-accent-700',
        )}
      >
        {isUser ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3 text-sm',
          isUser ? 'bg-ink-800 text-ivory-50' : 'bg-white border border-ivory-300 text-ink-900',
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        ) : (
          <>
            <MarkdownView markdown={content || ''} />
            {streaming && (
              <span className="inline-block w-1.5 h-4 ml-1 align-middle bg-accent-500 animate-blink" />
            )}
          </>
        )}
      </div>
    </motion.div>
  );
}
