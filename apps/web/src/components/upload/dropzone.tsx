'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, X, CheckCircle2 } from 'lucide-react';

import { ALLOWED_EXTENSIONS, MAX_UPLOAD_MB } from '@/lib/constants';
import { cn, formatBytes } from '@/lib/utils';

export interface UploadFileItem {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'done' | 'error';
  error?: string;
}

interface Props {
  onFiles: (files: File[]) => void;
  items: UploadFileItem[];
  onRemove: (id: string) => void;
}

export function Dropzone({ onFiles, items, onRemove }: Props) {
  const [hovering, setHovering] = useState(false);

  const onDrop = useCallback((accepted: File[]) => onFiles(accepted), [onFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDragEnter: () => setHovering(true),
    onDragLeave: () => setHovering(false),
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: MAX_UPLOAD_MB * 1024 * 1024,
    multiple: true,
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          'relative rounded-xl border-2 border-dashed transition-all p-12 text-center cursor-pointer',
          isDragActive || hovering
            ? 'border-accent-400 bg-accent-50/60'
            : 'border-ivory-300 bg-white hover:border-accent-300 hover:bg-ivory-50',
        )}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={{ y: isDragActive ? -4 : 0 }}
          className="mx-auto h-14 w-14 rounded-full bg-gradient-to-br from-accent-100 to-accent-50 border border-accent-200 grid place-items-center text-accent-600 mb-4"
        >
          <Upload className="h-6 w-6" />
        </motion.div>
        <p className="font-serif text-xl text-ink-900">Drop transcripts here</p>
        <p className="text-sm text-ink-600 mt-1">
          or <span className="text-accent-600 font-medium">browse files</span>
        </p>
        <p className="text-xs text-ink-500 mt-3">
          {ALLOWED_EXTENSIONS.join(', ').toUpperCase()} · up to {MAX_UPLOAD_MB} MB
        </p>
      </div>

      {items.length > 0 && (
        <div className="space-y-2">
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 rounded-lg border border-ivory-300 bg-white px-4 py-3"
            >
              <div className="h-9 w-9 rounded-md bg-ivory-100 grid place-items-center text-ink-600">
                <FileText className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-medium text-ink-900 truncate">{item.file.name}</div>
                  <div className="text-xs text-ink-500">{formatBytes(item.file.size)}</div>
                </div>
                <div className="h-1 mt-2 rounded-full bg-ivory-200 overflow-hidden">
                  <motion.div
                    className={cn(
                      'h-full rounded-full',
                      item.status === 'error' ? 'bg-destructive' : 'bg-accent-500',
                    )}
                    initial={{ width: 0 }}
                    animate={{ width: `${item.progress}%` }}
                    transition={{ ease: 'easeOut' }}
                  />
                </div>
                {item.error && <div className="text-xs text-destructive mt-1">{item.error}</div>}
              </div>
              {item.status === 'done' ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              ) : (
                <button
                  onClick={() => onRemove(item.id)}
                  className="p-1 rounded hover:bg-ivory-100 text-ink-500"
                  aria-label="Remove"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
