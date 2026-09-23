import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  CircleAlert,
  Crosshair,
  Gauge,
  Image as ImageIcon,
  Loader2,
  Play,
  RotateCcw,
  ShieldAlert,
  Timer,
  Trash2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { AppShell } from "@/components/sonar/AppShell";
import { DetectionCard } from "@/components/sonar/DetectionCard";
import { EmptyState } from "@/components/sonar/EmptyState";
import { StatCard } from "@/components/sonar/StatCard";
import { StatusPill } from "@/components/sonar/StatusPill";
import { UploadZone } from "@/components/sonar/UploadZone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  analyzeSonarImage,
  averageConfidence,
  confidencePercent,
  resolveAssetUrl,
  type AnalysisResult,
} from "@/lib/sonar-api";

const TITLE = "Sonar Image Analysis — SONAR-AI";
const DESCRIPTION =
  "Upload a side-scan sonar frame and run GhostVision YOLO26 inference to detect derelict fishing gear, with confidence, prototype risk and annotated output.";

export const Route = createFileRoute("/image-analysis")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: ImageAnalysis,
});

const ACCEPTED = ".jpg,.jpeg,.png,.tif,.tiff,image/jpeg,image/png,image/tiff";
const VALID_EXT = /\.(jpe?g|png|tiff?)$/i;

type Phase = "idle" | "ready" | "running" | "done" | "error";

function ImageAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    if (phase !== "running") return;
    setProgress(8);
    const id = setInterval(() => setProgress((p) => (p < 90 ? p + 6 : p)), 260);
    return () => clearInterval(id);
  }, [phase]);

  const reset = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setProgress(0);
    setPhase("idle");
  };

  const handleFile = (next: File) => {
    if (!VALID_EXT.test(next.name)) {
      setError("Unsupported file. Use a JPG, PNG or TIFF sonar frame.");
      setPhase("error");
      return;
    }
    setFile(next);
    setResult(null);
    setError(null);
    setProgress(0);
    setPhase("ready");
  };

  const runAnalysis = async () => {
    if (!file) return;
    setPhase("running");
    setError(null);
    setResult(null);
    try {
      const data = await analyzeSonarImage(file);
      setResult({ source: "backend", data });
      setProgress(100);
      setPhase("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed.");
      setPhase("error");
    }
  };

  const detections = result?.data.detections ?? [];
  const annotated = useMemo(
    () => resolveAssetUrl(result?.data.annotated_image),
    [result?.data.annotated_image],
  );
  const avgConfidence = confidencePercent(averageConfidence(detections));

  return (
    <AppShell>
      <div className="space-y-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Sonar Image Analysis</h1>
            <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
              Current AI prototype: derelict fishing-gear detection from side-scan sonar imagery.
              Results come straight from the GhostVision YOLO26 engine.
            </p>
          </div>
          {file && (
            <Button variant="outline" size="sm" onClick={reset}>
              <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
              New analysis
            </Button>
          )}
        </header>

        {!file ? (
          <UploadZone
            accept={ACCEPTED}
            title="Drop a sonar frame to analyse"
            hint="JPG, PNG or TIFF side-scan imagery. The file is sent to the AI engine for real inference."
            onFile={handleFile}
          />
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1.15fr_1fr]">
            <Card className="border-border/70 bg-surface">
              <CardHeader className="flex-row items-center justify-between gap-3 pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <ImageIcon className="h-4 w-4 text-primary" />
                  {annotated ? "Annotated output" : "Uploaded frame"}
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={reset}>
                  <Trash2 className="mr-1.5 h-3.5 w-3.5" />
                  Remove
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="overflow-hidden rounded-lg border border-border/70 bg-background">
                  {annotated ? (
                    <img src={annotated} alt="Annotated sonar frame with detected targets" className="w-full" />
                  ) : previewUrl ? (
                    <img src={previewUrl} alt={`Sonar frame ${file.name}`} className="w-full" />
                  ) : null}
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[11px] text-muted-foreground">
                  <span className="truncate">{file.name}</span>
                  <span>{(file.size / 1024).toFixed(0)} KB</span>
                </div>

                {phase === "running" && (
                  <div className="space-y-2">
                    <Progress value={progress} className="h-1.5 bg-secondary" />
                    <p className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                      Running inference on the AI engine…
                    </p>
                  </div>
                )}

                {phase !== "done" && (
                  <Button
                    className="w-full"
                    size="lg"
                    onClick={runAnalysis}
                    disabled={phase === "running"}
                  >
                    {phase === "running" ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="mr-2 h-4 w-4" />
                    )}
                    {phase === "running" ? "Analysing…" : "Run detection"}
                  </Button>
                )}
              </CardContent>
            </Card>

            <div className="space-y-4">
              {error && (
                <div className="flex items-start gap-3 rounded-lg border border-danger/45 bg-danger/10 p-4 text-sm text-danger">
                  <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" />
                  <div className="space-y-2">
                    <p className="font-semibold">Analysis could not complete</p>
                    <p className="text-danger/90">{error}</p>
                    {file && (
                      <Button variant="outline" size="sm" onClick={runAnalysis}>
                        <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
                        Retry
                      </Button>
                    )}
                  </div>
                </div>
              )}

              {result ? (
                <>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <StatCard
                      label="Targets"
                      value={result.data.summary.total_targets ?? detections.length}
                      icon={Crosshair}
                      tone="primary"
                    />
                    <StatCard
                      label="High risk"
                      value={result.data.summary.high_risk_targets ?? 0}
                      icon={ShieldAlert}
                      tone={(result.data.summary.high_risk_targets ?? 0) > 0 ? "danger" : "ok"}
                    />
                    <StatCard
                      label="Avg confidence"
                      value={`${avgConfidence.toFixed(1)}%`}
                      icon={Gauge}
                    />
                    <StatCard
                      label="Processing time"
                      value={`${Number(result.data.summary.processing_time ?? 0).toFixed(2)}s`}
                      icon={Timer}
                    />
                  </div>

                  <Card className="border-border/70 bg-surface">
                    <CardHeader className="flex-row items-center justify-between gap-3 pb-3">
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Activity className="h-4 w-4 text-primary" />
                        Target list
                      </CardTitle>
                      <StatusPill tone={result.source === "backend" ? "ok" : "warn"}>
                        {result.source === "backend" ? "Model output" : "Demo / simulated"}
                      </StatusPill>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {detections.length === 0 ? (
                        <EmptyState
                          icon={Crosshair}
                          title="No targets detected"
                          description="The model found no Crab-Pot signatures in this frame. Try a frame with clearer seabed contrast or a different gain setting."
                        />
                      ) : (
                        detections.map((d, i) => (
                          <DetectionCard
                            key={`${d.label}-${i}`}
                            detection={d}
                            index={i}
                            simulated={result.source === "demo"}
                          />
                        ))
                      )}
                      <p className="pt-1 text-xs text-muted-foreground">
                        Risk is a prototype heuristic based on detection confidence, not a validated
                        marine-hazard risk model.
                      </p>
                    </CardContent>
                  </Card>
                </>
              ) : (
                !error && (
                  <EmptyState
                    icon={Activity}
                    title="No results yet"
                    description="Run detection to see targets, confidence, prototype risk and the annotated frame returned by the AI engine."
                  />
                )
              )}
            </div>
          </div>
        )}

        {phase === "error" && !file && error && (
          <div className="flex items-start gap-3 rounded-lg border border-danger/45 bg-danger/10 p-4 text-sm text-danger">
            <CircleAlert className="mt-0.5 h-4 w-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
