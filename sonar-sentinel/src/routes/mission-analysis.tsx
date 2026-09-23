import { createFileRoute, Link } from "@tanstack/react-router";
import { FileStack, Info, Waves, Wrench } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/sonar/AppShell";
import { PipelineFlow } from "@/components/sonar/PipelineFlow";
import { StatusPill } from "@/components/sonar/StatusPill";
import { UploadZone } from "@/components/sonar/UploadZone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TITLE = "Mission Analysis — Sonar Log Pipeline | SONAR-AI";
const DESCRIPTION =
  "The intended XTF/JSF sonar log pipeline for SONAR-AI: ping and navigation extraction, frame generation, YOLO26 detection, target validation, geolocation and mission reporting.";

export const Route = createFileRoute("/mission-analysis")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: MissionAnalysis,
});

function MissionAnalysis() {
  const [queued, setQueued] = useState<string | null>(null);

  return (
    <AppShell>
      <div className="space-y-6">
        <header>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold">Mission Analysis</h1>
            <StatusPill tone="warn">Prototype / Integration Ready</StatusPill>
          </div>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Full sonar-log processing is the next backend step. Logs accepted here are queued and
            described only — no processing is simulated and no coordinates are generated. For a
            working detection run today, use single-frame image analysis.
          </p>
        </header>

        <UploadZone
          accept=".xtf,.jsf"
          title="Select an XTF / JSF sonar log"
          hint="Mission-level workflow. The parser is not connected yet, so the file is registered locally and not processed."
          onFile={(file) => setQueued(`${file.name} · ${(file.size / 1024 / 1024).toFixed(1)} MB`)}
        />

        {queued && (
          <div className="flex flex-wrap items-center gap-3 rounded-lg border border-warn/40 bg-warn/8 p-4 text-sm text-warn">
            <FileStack className="h-4 w-4 shrink-0" />
            <span className="font-mono text-xs">{queued}</span>
            <span>Registered. Log parsing arrives with the backend pipeline — nothing was analysed.</span>
            <Button variant="ghost" size="sm" className="ml-auto" onClick={() => setQueued(null)}>
              Clear
            </Button>
          </div>
        )}

        <Card className="border-border/70 bg-surface">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Waves className="h-4 w-4 text-primary" />
              Intended pipeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="font-mono text-xs leading-relaxed text-muted-foreground">
              Sonar Log → Ping/Navigation Extraction → Frame Generation → Preprocessing → YOLO26
              Detection → Target Validation → Geolocation → Mission Report
            </p>
            <PipelineFlow />
          </CardContent>
        </Card>

        <Card className="border-border/70 bg-surface">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Wrench className="h-4 w-4 text-primary" />
              What connecting the pipeline requires
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p>
              A log endpoint on the FastAPI service that streams ping records, emits waterfall
              frames, and runs the existing ONNX detector frame by frame.
            </p>
            <p>
              Navigation records to convert pixel boxes into positions — until then the map shows
              schematic, clearly labelled demo markers only.
            </p>
            <p className="flex items-start gap-2 rounded-lg border border-primary/25 bg-primary/8 p-3 text-foreground/90">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
              <span>
                The detection stage is already live and proven on single frames, so log support is
                an ingestion problem rather than a model problem.
              </span>
            </p>
            <Button asChild variant="outline" size="sm">
              <Link to="/image-analysis">Run a single-frame detection now</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
