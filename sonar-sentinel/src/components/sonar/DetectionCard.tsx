import { Crosshair } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import { confidencePercent, type Detection } from "@/lib/sonar-api";
import { cn } from "@/lib/utils";

function riskTone(risk: string) {
  const value = risk?.toLowerCase?.() ?? "";
  if (value.includes("high")) return "border-danger/45 bg-danger/10 text-danger";
  if (value.includes("med")) return "border-warn/45 bg-warn/10 text-warn";
  if (value.includes("low")) return "border-ok/45 bg-ok/10 text-ok";
  return "border-border bg-secondary text-muted-foreground";
}

export function DetectionCard({
  detection,
  index,
  simulated = false,
}: {
  detection: Detection;
  index: number;
  simulated?: boolean;
}) {
  const pct = confidencePercent(detection.confidence);

  return (
    <div className="rounded-lg border border-border/70 bg-surface p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="rounded-md border border-border/70 bg-surface-raised p-2 text-primary">
            <Crosshair className="h-4 w-4" />
          </span>
          <div>
            <p className="text-sm font-semibold">{detection.label || "Unclassified"}</p>
            <p className="font-mono text-[11px] tracking-wide text-muted-foreground uppercase">
              Target {String(index + 1).padStart(2, "0")}
              {simulated && " · simulated"}
            </p>
          </div>
        </div>
        <span
          className={cn(
            "rounded-full border px-2 py-0.5 font-mono text-[10px] tracking-widest uppercase",
            riskTone(detection.risk),
          )}
        >
          {detection.risk || "n/a"} risk
        </span>
      </div>

      <div className="mt-4 space-y-1.5">
        <div className="flex items-center justify-between font-mono text-[11px] text-muted-foreground">
          <span>CONFIDENCE</span>
          <span className="text-foreground tabular-nums">{pct.toFixed(1)}%</span>
        </div>
        <Progress value={pct} className="h-1.5 bg-secondary" />
      </div>

      <p className="mt-3 font-mono text-[10px] break-all text-muted-foreground">
        BOX [{detection.box?.map((n) => Math.round(n)).join(", ")}]
      </p>
    </div>
  );
}
