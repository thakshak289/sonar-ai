import { cn } from "@/lib/utils";

/** Tasteful sonar sweep dial used in the dashboard header. */
export function RadarDial({ className }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={cn(
        "relative aspect-square w-full overflow-hidden rounded-full border border-primary/25 bg-background/60",
        className,
      )}
    >
      {[0.32, 0.58, 0.84].map((scale) => (
        <div
          key={scale}
          className="absolute inset-0 m-auto rounded-full border border-primary/15"
          style={{ width: `${scale * 100}%`, height: `${scale * 100}%` }}
        />
      ))}
      <div className="absolute inset-x-0 top-1/2 h-px bg-primary/12" />
      <div className="absolute inset-y-0 left-1/2 w-px bg-primary/12" />

      <div className="radar-sweep absolute inset-0 origin-center">
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background:
              "conic-gradient(from 0deg, color-mix(in oklch, var(--primary) 34%, transparent), transparent 70deg, transparent 360deg)",
          }}
        />
      </div>

      <div className="ping-ring absolute inset-0 m-auto h-2/3 w-2/3 rounded-full border border-primary/40" />
      <div className="absolute inset-0 m-auto h-1.5 w-1.5 rounded-full bg-primary" />
    </div>
  );
}
