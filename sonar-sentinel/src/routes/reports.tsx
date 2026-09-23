import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, FileText, ListChecks } from "lucide-react";

import { AppShell } from "@/components/sonar/AppShell";
import { EmptyState } from "@/components/sonar/EmptyState";
import { StatusPill } from "@/components/sonar/StatusPill";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TITLE = "Mission Reports — SONAR-AI";
const DESCRIPTION =
  "Planned SONAR-AI mission report: survey summary, detected targets, confidence and prototype risk, coordinates when navigation data is available, and export.";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: Reports,
});

const FIELDS = [
  { name: "Survey summary", detail: "Mission ID, log file, frames processed, coverage duration" },
  { name: "Detected targets", detail: "Class (Crab-Pot), frame index, bounding box" },
  { name: "Confidence & risk", detail: "Model confidence plus prototype confidence-based risk tier" },
  { name: "Coordinates", detail: "Latitude / longitude — only when log navigation data is parsed" },
  { name: "Annotated evidence", detail: "Annotated frames returned by the detection engine" },
  { name: "Export", detail: "PDF / CSV mission report for field and enforcement teams" },
];

function Reports() {
  return (
    <AppShell>
      <div className="space-y-6">
        <header>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold">Mission Reports</h1>
            <StatusPill tone="warn">Coming next</StatusPill>
          </div>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Reports are generated from a completed log mission. Since log processing is the next
            backend step, no report data exists yet — the fields below define the output format.
          </p>
        </header>

        <Card className="border-border/70 bg-surface">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <ListChecks className="h-4 w-4 text-primary" />
              Planned report fields
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            {FIELDS.map((f) => (
              <div key={f.name} className="rounded-lg border border-border/70 bg-surface-raised p-4">
                <p className="text-sm font-semibold">{f.name}</p>
                <p className="mt-1 text-xs text-muted-foreground">{f.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <EmptyState
          icon={FileText}
          title="No mission reports yet"
          description="Complete a sonar log mission to generate a report. Single-frame detections can be reviewed in the image analysis workspace today."
          action={
            <div className="flex flex-wrap justify-center gap-2">
              <Button asChild variant="outline" size="sm">
                <Link to="/image-analysis">Analyze Sonar Image</Link>
              </Button>
              <Button size="sm" disabled>
                <Download className="mr-1.5 h-3.5 w-3.5" />
                Export report
              </Button>
            </div>
          }
        />
      </div>
    </AppShell>
  );
}
