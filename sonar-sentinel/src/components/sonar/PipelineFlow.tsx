import { CircleDashed, CircleCheck, ChevronRight } from "lucide-react";

import { cn } from "@/lib/utils";

export interface PipelineStage {
  name: string;
  detail: string;
  status: "ready" | "planned";
}

export const LOG_PIPELINE: PipelineStage[] = [
  { name: "Sonar Log", detail: "XTF / JSF file intake", status: "planned" },
  { name: "Ping & Navigation Extraction", detail: "Per-ping returns + nav records", status: "planned" },
  { name: "Frame Generation", detail: "Waterfall frames from ping stacks", status: "planned" },
  { name: "Preprocessing", detail: "Slant-range / gain normalisation", status: "planned" },
  { name: "YOLO26 Detection", detail: "GhostVision ONNX inference", status: "ready" },
  { name: "Target Validation", detail: "De-duplication across frames", status: "planned" },
  { name: "Geolocation", detail: "Pixel → lat/lon from nav data", status: "planned" },
  { name: "Mission Report", detail: "Survey summary + export", status: "planned" },
];

export function PipelineFlow({ stages = LOG_PIPELINE }: { stages?: PipelineStage[] }) {
  return (
    <ol className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {stages.map((stage, i) => {
        const ready = stage.status === "ready";
        const Icon = ready ? CircleCheck : CircleDashed;
        return (
          <li
            key={stage.name}
            className={cn(
              "relative rounded-lg border bg-surface p-4",
              ready ? "border-ok/40" : "border-border/70",
            )}
          >
            <div className="flex items-center gap-2">
              <Icon className={cn("h-4 w-4", ready ? "text-ok" : "text-muted-foreground")} />
              <span className="font-mono text-[10px] tracking-widest text-muted-foreground">
                STEP {String(i + 1).padStart(2, "0")}
              </span>
              {i < stages.length - 1 && (
                <ChevronRight className="ml-auto hidden h-4 w-4 text-border xl:block" />
              )}
            </div>
            <p className="mt-2 text-sm font-semibold">{stage.name}</p>
            <p className="mt-1 text-xs text-muted-foreground">{stage.detail}</p>
            <p
              className={cn(
                "mt-3 font-mono text-[10px] tracking-widest uppercase",
                ready ? "text-ok" : "text-warn",
              )}
            >
              {ready ? "model connected" : "integration ready"}
            </p>
          </li>
        );
      })}
    </ol>
  );
}
