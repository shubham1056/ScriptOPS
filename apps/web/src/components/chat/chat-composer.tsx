'use client';

import { Loader2, Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { Button } from '@/components/ui/button';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatComposer({ onSend, disabled }: Props) {
  const [text, setText] = useState('');
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = 'auto';
    ref.current.style.height = Math.min(ref.current.scrollHeight, 200) + 'px';
  }, [text]);

  const submit = () => {
    const v = text.trim();
    if (!v || disabled) return;
    onSend(v);
    setText('');
  };

  return (
    <div className="relative rounded-2xl border border-ivory-300 bg-white shadow-soft focus-within:border-accent-400 focus-within:ring-2 focus-within:ring-ring transition">
      <textarea
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        rows={1}
        placeholder="Ask TranscribeOP to refine, summarize, or extract a workflow…"
        className="w-full resize-none bg-transparent px-4 py-3.5 pr-14 text-sm outline-none placeholder:text-ink-400 max-h-[200px]"
      />
      <Button
        size="icon"
        className="absolute right-2 bottom-2 h-9 w-9 rounded-xl"
        onClick={submit}
        disabled={disabled || !text.trim()}
        aria-label="Send"
      >
        {disabled ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
      </Button>
    </div>
  );
}
