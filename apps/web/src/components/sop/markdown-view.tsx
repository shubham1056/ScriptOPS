'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { cn } from '@/lib/utils';

interface Props {
  markdown: string;
  className?: string;
}

export function MarkdownView({ markdown, className }: Props) {
  return (
    <article className={cn('prose-claude max-w-none', className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
    </article>
  );
}
