import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Cpu,
  FileText,
  Image as ImageIcon,
  Info,
  Map as MapIcon,
  ShieldAlert,
  Waves,
} from "lucide-react";

import { AppShell } from "@/components/sonar/AppShell";
import { RadarDial } from "@/components/sonar/RadarDial";
import { StatusPill } from "@/components/sonar/StatusPill";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useBackendStatus } from "@/hooks/use-backend-status";

const TITLE = "SONAR-AI — Intelligent Marine Debris Detection & Geospatial Analysis";
const DESCRIPTION =
  "SONAR-AI analyses side-scan sonar imagery with a GhostVision YOLO26 ONNX model to flag derelict fishing gear, with a mission pipeline for full sonar log surveys.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: Dashboard,
});

const CAPABILITIES = [
  {
    icon: ImageIcon,
    title: "Sonar Image Detection",
    body: "Upload a JPG, PNG or TIFF sonar frame and run live inference on the AI engine.",
    status: "Live",
    tone: "ok" as const,
  },
  {
    icon: Waves,
    title: "Sonar Log Missions",
    body: "XTF / JSF survey logs with ping and navigation extraction across a whole mission.",
    status: "Integration ready",
    tone: "warn" as const,
  },
  {
    icon: MapIcon,
    title: "Geospatial Targets",
    body: "Target positions derived from navigation records once log parsing is connected.",
    status: "Coming next",
    tone: "warn" as const,
  },
  {
    icon: FileText,
    title: "Mission Reports",
    body: "Survey summary, target table, confidence and risk, exportable for field teams.",
    status: "Coming next",
    tone: "warn" as const,
  },
];

function Dashboard() {
  const { status } = useBackendStatus();

  return (
    <AppShell>
      <div className="space-y-8">
        <section className="sonar-grid panel-glow overflow-hidden rounded-2xl border border-border/70 bg-surface/70">
          <div className="grid items-center gap-8 p-6 sm:p-8 lg:grid-cols-[1.5fr_1fr]">
            <div>
              <StatusPill tone={status === "online" ? "ok" : "muted"} pulse={status === "online"}>
                {status === "online"
                  ? "AI Engine Online"
                  : status === "checking"
                    ? "Contacting Engine"
                    : "AI Engine Offline"}
              </StatusPill>

              <h1 className="mt-4 font-mono text-3xl font-bold tracking-tight sm:text-4xl">
                SONAR-AI
              </h1>
              <p className="mt-2 max-w-xl text-base text-muted-foreground sm:text-lg">
                Intelligent marine debris detection and geospatial analysis for side-scan sonar
                surveys.
              </p>

              <p className="mt-4 flex max-w-xl items-start gap-2 rounded-lg border border-primary/25 bg-primary/8 p-3 text-sm text-foreground/90">
                <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                <span>
                  Current AI prototype: derelict fishing-gear detection from side-scan sonar imagery
                  (single class: <span className="font-mono">Crab-Pot</span>). Broader marine-debris
                  classes are the product roadmap, not the shipped model.
                </span>
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Button asChild size="lg">
                  <Link to="/image-analysis">
                    <ImageIcon className="mr-2 h-4 w-4" />
                    Analyze Sonar Image
                  </Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/mission-analysis">
                    <Waves className="mr-2 h-4 w-4" />
                    Analyze Sonar Log
                  </Link>
                </Button>
              </div>
            </div>

            <div className="mx-auto w-full max-w-[260px]">
              <RadarDial />
              <p className="mt-3 text-center font-mono text-[10px] tracking-widest text-muted-foreground uppercase">
                sweep visual · not live sonar
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {CAPABILITIES.map(({ icon: Icon, title, body, status: label, tone }) => (
            <Card key={title} className="border-border/70 bg-surface">
              <CardContent className="p-5">
                <span className="inline-flex rounded-md border border-border/70 bg-surface-raised p-2 text-primary">
                  <Icon className="h-4 w-4" />
                </span>
                <p className="mt-3 text-sm font-semibold">{title}</p>
                <p className="mt-1 text-sm text-muted-foreground">{body}</p>
                <StatusPill tone={tone} className="mt-4">
                  {label}
                </StatusPill>
              </CardContent>
            </Card>
          ))}
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <Card className="border-border/70 bg-surface">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="h-4 w-4 text-primary" />
                Detection engine
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <Row label="Model" value="GhostVision YOLO26" />
              <Row label="Runtime" value="ONNX Runtime (FastAPI service)" />
              <Row label="Trained class" value="Crab-Pot" />
              <Row label="Input" value="Side-scan sonar frames (JPG / PNG / TIFF)" />
              <Row label="Log formats" value="XTF / JSF — parser integration pending" />
            </CardContent>
          </Card>

          <Card className="border-border/70 bg-surface">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <ShieldAlert className="h-4 w-4 text-warn" />
                Prototype limits we are explicit about
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-muted-foreground">
              <p>
                Risk levels are a prototype heuristic derived from detection confidence, not a
                scientifically validated marine-hazard risk model.
              </p>
              <p>
                No GPS coordinates are generated by this build. Any map position shown is labelled
                DEMO / SIMULATED until real navigation records are parsed.
              </p>
              <p>
                Detections shown anywhere in the app come from the backend model. Nothing is
                inferred or synthesised in the browser.
              </p>
              <Button asChild variant="ghost" size="sm" className="px-0 text-primary">
                <Link to="/mission-analysis">
                  See the intended mission pipeline
                  <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </section>
      </div>
    </AppShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-border/50 pb-2 last:border-0">
      <span className="font-mono text-[11px] tracking-widest text-muted-foreground uppercase">
        {label}
      </span>
      <span className="text-right text-sm">{value}</span>
    </div>
  );
}
