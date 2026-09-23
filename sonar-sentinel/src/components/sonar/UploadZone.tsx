import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { cn } from "@/lib/utils";

export function UploadZone({
  accept,
  hint,
  title,
  disabled = false,
  onFile,
}: {
  accept: string;
  title: string;
  hint: string;
  disabled?: boolean;
  onFile: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={(e) => {
        if (disabled) return;
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          inputRef.current?.click();
        }
      }}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (disabled) return;
        const file = e.dataTransfer.files?.[0];
        if (file) onFile(file);
      }}
      className={cn(
        "sonar-grid flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-border/80 bg-surface/60 px-6 py-14 text-center transition-colors outline-none",
        !disabled && "cursor-pointer hover:border-primary/60 hover:bg-surface",
        dragging && "border-primary bg-primary/5",
        disabled && "opacity-60",
        "focus-visible:ring-2 focus-visible:ring-ring",
      )}
    >
      <span className="rounded-full border border-primary/30 bg-primary/10 p-4 text-primary">
        <UploadCloud className="h-7 w-7" />
      </span>
      <p className="mt-4 text-base font-semibold">{title}</p>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">{hint}</p>
      <p className="mt-4 font-mono text-[11px] tracking-widest text-muted-foreground uppercase">
        drag &amp; drop or click to browse
      </p>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.target.value = "";
        }}
      />
    </div>
  );
}
