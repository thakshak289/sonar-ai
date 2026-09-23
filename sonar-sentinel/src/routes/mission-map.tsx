import { createFileRoute, Link } from "@tanstack/react-router";
import { Compass, MapPin, Radio, Ship } from "lucide-react";
import { useState } from "react";

import { AppShell } from "@/components/sonar/AppShell";
import { StatusPill } from "@/components/sonar/StatusPill";
import { SurveyMap } from "@/components/sonar/SurveyMap";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DEMO_MISSION } from "@/lib/demo-mission";

const TITLE = "Mission Map — Survey Overview | SONAR-AI";
const DESCRIPTION =
  "Schematic survey-track view for SONAR-AI missions. Target markers are demo/simulated placeholders until sonar-log navigation parsing supplies real positions.";

export const Route = createFileRoute("/mission-map")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESCRIPTION },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESCRIPTION },
    ],
  }),
  component: MissionMap,
});

function MissionMap() {
  const [demo, setDemo] = useState(false);

  return (
    <AppShell>
      <div className="space-y-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-semibold">Mission Map</h1>
              <StatusPill tone={demo ? "warn" : "muted"}>
                {demo ? "Demo mission active" : "No mission loaded"}
              </StatusPill>
            </div>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
              Real target positions require navigation records from an XTF/JSF log. This view is a
              schematic survey layout — it never displays invented GPS coordinates.
            </p>
          </div>
          <Button variant={demo ? "outline" : "default"} onClick={() => setDemo((v) => !v)}>
            <Radio className="mr-2 h-4 w-4" />
            {demo ? "Exit demo mission" : "Launch Demo Mission"}
          </Button>
        </header>

        <div className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
          <Card className="border-border/70 bg-surface">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Compass className="h-4 w-4 text-primary" />
                Survey overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <SurveyMap showMarkers={demo} />
            </CardContent>
          </Card>

          <Card className="border-border/70 bg-surface">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Ship className="h-4 w-4 text-primary" />
                Mission details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {demo ? (
                <>
                  <Row label="Mission" value={DEMO_MISSION.name} />
                  <Row label="Platform" value={DEMO_MISSION.vessel} />
                  <Row label="Pattern" value={DEMO_MISSION.survey} />
                  <Row label="Contacts" value={`${DEMO_MISSION.markers.length} (simulated)`} />
                  <Row label="Coordinates" value="Not available" />
                  <div className="space-y-2 rounded-lg border border-warn/35 bg-warn/8 p-3 text-xs text-warn">
                    <p className="flex items-center gap-2 font-semibold">
                      <MapPin className="h-3.5 w-3.5" /> DEMO / SIMULATED LOCATION
                    </p>
                    <p>
                      Markers are layout placeholders. They are not model detections and carry no
                      geographic meaning.
                    </p>
                  </div>
                  {DEMO_MISSION.sampleImageUrl ? (
                    <Button asChild size="sm" className="w-full">
                      <Link to="/image-analysis">Analyse bundled sample frame</Link>
                    </Button>
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      No bundled sample sonar frame is included yet. Once added, it plugs into this
                      demo without any layout change.
                    </p>
                  )}
                </>
              ) : (
                <>
                  <p className="text-muted-foreground">
                    Load the demo mission to preview how survey tracks and validated targets will be
                    laid out, or run a single-frame detection for live model output.
                  </p>
                  <Button asChild variant="outline" size="sm" className="w-full">
                    <Link to="/image-analysis">Analyze Sonar Image</Link>
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-border/50 pb-2">
      <span className="font-mono text-[11px] tracking-widest text-muted-foreground uppercase">
        {label}
      </span>
      <span className="text-right text-sm">{value}</span>
    </div>
  );
}
