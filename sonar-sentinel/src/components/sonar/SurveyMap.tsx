import { MapPin, TriangleAlert } from "lucide-react";

import { DEMO_MISSION, DEMO_DISCLAIMER } from "@/lib/demo-mission";

/**
 * Survey-track visual. Purely a schematic — it renders no real coordinates and
 * every marker is explicitly labelled as a simulated location.
 */
export function SurveyMap({ showMarkers = false }: { showMarkers?: boolean }) {
  const track = DEMO_MISSION.track;
  const points = track.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className="space-y-3">
      <div className="sonar-grid relative aspect-[16/9] w-full overflow-hidden rounded-xl border border-border/70 bg-background/70">
        <div
          className="absolute inset-0 opacity-70"
          style={{
            background:
              "radial-gradient(circle at 50% 55%, color-mix(in oklch, var(--primary) 12%, transparent), transparent 65%)",
          }}
        />
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
          <polyline
            points={points}
            fill="none"
            stroke="color-mix(in oklch, var(--primary) 70%, transparent)"
            strokeWidth="0.5"
            strokeDasharray="2 1.5"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        {showMarkers &&
          DEMO_MISSION.markers.map((m) => (
            <div
              key={m.label}
              className="absolute -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${m.x}%`, top: `${m.y}%` }}
            >
              <div className="flex flex-col items-center gap-1">
                <MapPin className="h-5 w-5 text-warn drop-shadow" />
                <span className="rounded border border-warn/40 bg-background/85 px-1.5 py-0.5 font-mono text-[9px] tracking-widest text-warn uppercase whitespace-nowrap">
                  {m.label} · demo
                </span>
              </div>
            </div>
          ))}

        <span className="absolute top-3 left-3 rounded border border-border bg-background/80 px-2 py-1 font-mono text-[10px] tracking-widest text-muted-foreground uppercase">
          survey track · schematic
        </span>
      </div>

      <p className="flex items-start gap-2 rounded-lg border border-warn/35 bg-warn/8 p-3 text-xs text-warn">
        <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />
        <span>{DEMO_DISCLAIMER}</span>
      </p>
    </div>
  );
}
