import { cn } from '@/lib/utils';

export function BrandMark({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <div className="relative h-8 w-8 rounded-lg bg-gradient-to-br from-accent-500 to-accent-700 shadow-soft grid place-items-center">
        <span className="font-serif text-white text-base leading-none">T</span>
        <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-accent-400 ring-2 ring-ivory-50" />
      </div>
      <div className="flex flex-col leading-tight">
        <span className="font-serif text-[17px] text-ink-900">TranscribeOP</span>
        <span className="text-[10px] uppercase tracking-[0.16em] text-ink-400">SOP Intelligence</span>
      </div>
    </div>
  );
}
