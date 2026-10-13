import { AlertCircle, CheckCircle2, FileText, UploadCloud, X } from 'lucide-react';
import type { ChangeEvent, DragEvent } from 'react';
import { useRef, useState } from 'react';

interface FileUploadCardProps {
  label: string;
  description: string;
  file: File | null;
  onSelect: (file: File) => void;
  onRemove: () => void;
  error?: string;
}

const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export function FileUploadCard({ label, description, file, onSelect, onRemove, error }: FileUploadCardProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleInput = (event: ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (selected) {
      onSelect(selected);
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const selected = event.dataTransfer.files?.[0];
    if (selected) {
      onSelect(selected);
    }
  };

  return (
    <div className={`panel overflow-hidden ${file ? 'border-blue/30' : ''}`}>
      <div
        className={`flex w-full flex-col gap-4 p-4 text-left transition ${isDragging ? 'bg-blue/5' : 'hover:bg-slate-50/70'} ${error ? 'border border-red-200' : ''}`}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <div className="flex items-start justify-between gap-3">
          <button
            type="button"
            className="flex items-start gap-3 text-left"
            onClick={() => inputRef.current?.click()}
          >
            <div className={`rounded-xl p-2 ${file ? 'bg-emerald-100 text-emerald-700' : 'bg-blue/10 text-blue'}`}>
              {file ? <CheckCircle2 size={18} /> : <UploadCloud size={18} />}
            </div>
            <div>
              <div className="text-base font-semibold text-text">{label}</div>
              <div className="mt-1 text-sm text-slate-500">{description}</div>
            </div>
          </button>

          {file && (
            <button
              type="button"
              className="rounded-lg border border-border p-1.5 text-slate-500 transition hover:border-red-200 hover:text-red-600"
              onClick={(event) => {
                event.stopPropagation();
                onRemove();
              }}
              aria-label={`Remove ${label}`}
            >
              <X size={16} />
            </button>
          )}
        </div>

        <button
          type="button"
          className="flex items-center justify-between gap-3 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-3 text-left"
          onClick={() => inputRef.current?.click()}
        >
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <FileText size={18} className="text-blue" />
            {file ? (
              <div>
                <div className="font-medium text-text">{file.name}</div>
                <div className="text-xs text-slate-500">{formatBytes(file.size)}</div>
              </div>
            ) : (
              <span>Click to select a PDF</span>
            )}
          </div>
          {file ? (
            <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-medium text-emerald-700">Selected</span>
          ) : (
            <span className="rounded-full bg-blue/10 px-2.5 py-1 text-xs font-medium text-blue">Awaiting file</span>
          )}
        </button>

        {error && (
          <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}
      </div>

      <input ref={inputRef} type="file" accept="application/pdf" className="hidden" onChange={handleInput} />
    </div>
  );
}
