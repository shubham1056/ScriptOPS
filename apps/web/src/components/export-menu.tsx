'use client';

import { ChevronDown, Download, FileCode2, FileText, FileType2, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import { Button, type ButtonProps } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { apiClient } from '@/lib/api/client';

type Format = 'md' | 'docx' | 'pdf';

interface ExportMenuProps {
  /** API path under /api/v1, e.g. `/sops/<id>/download` or `/conversations/<id>/download`. */
  endpoint: string;
  /** Used to derive a download filename if the server doesn't send one. */
  filenameHint: string;
  /** Button label. Default: "Download". */
  label?: string;
  /** Optional list of formats to expose (default: all three). */
  formats?: Format[];
  /** Disable the trigger (e.g. SOP not yet generated). */
  disabled?: boolean;
  /** shadcn Button variant, default 'default'. */
  variant?: ButtonProps['variant'];
  /** Button size, default 'default'. */
  size?: ButtonProps['size'];
}

const FORMAT_META: Record<Format, { label: string; ext: string; Icon: typeof FileText }> = {
  md: { label: 'Markdown (.md)', ext: 'md', Icon: FileCode2 },
  docx: { label: 'Word (.docx)', ext: 'docx', Icon: FileText },
  pdf: { label: 'PDF (.pdf)', ext: 'pdf', Icon: FileType2 },
};

function slugify(s: string) {
  return s.replace(/[^A-Za-z0-9._-]+/g, '_').replace(/^_+|_+$/g, '') || 'export';
}

function filenameFromResponse(headers: Record<string, string>, hint: string, fmt: Format): string {
  const disposition = headers['content-disposition'] || headers['Content-Disposition'];
  if (disposition) {
    const match = /filename\*?=(?:UTF-8'')?["']?([^"';]+)/i.exec(disposition);
    if (match?.[1]) return decodeURIComponent(match[1]);
  }
  return `${slugify(hint)}.${FORMAT_META[fmt].ext}`;
}

export function ExportMenu({
  endpoint,
  filenameHint,
  label = 'Download',
  formats = ['md', 'docx', 'pdf'],
  disabled,
  variant = 'default',
  size = 'default',
}: ExportMenuProps) {
  const [busyFmt, setBusyFmt] = useState<Format | null>(null);

  const onPick = async (fmt: Format) => {
    if (busyFmt) return;
    setBusyFmt(fmt);
    try {
      const res = await apiClient.get(endpoint, {
        params: { fmt },
        responseType: 'blob',
      });
      const filename = filenameFromResponse(
        res.headers as Record<string, string>,
        filenameHint,
        fmt,
      );
      const url = URL.createObjectURL(res.data as Blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      const msg =
        err?.response?.status === 409
          ? 'Nothing to download yet.'
          : err?.response?.status === 404
            ? 'Not found.'
            : 'Download failed.';
      toast.error(msg);
    } finally {
      setBusyFmt(null);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} disabled={disabled || !!busyFmt}>
          {busyFmt ? <Loader2 className="animate-spin" /> : <Download />}
          {label}
          <ChevronDown className="opacity-60" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Export as</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {formats.map((fmt) => {
          const { label: itemLabel, Icon } = FORMAT_META[fmt];
          return (
            <DropdownMenuItem
              key={fmt}
              onSelect={(e) => {
                e.preventDefault();
                void onPick(fmt);
              }}
              disabled={!!busyFmt}
            >
              {busyFmt === fmt ? <Loader2 className="animate-spin" /> : <Icon />}
              {itemLabel}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
