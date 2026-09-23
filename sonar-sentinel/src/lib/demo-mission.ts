/**
 * Demo mission scaffolding.
 *
 * Holds NO model output. Detections are only ever produced by the backend.
 * Real sample sonar imagery can be dropped into `sampleImageUrl` later
 * without touching any page layout.
 */

export interface DemoMarker {
  /** Percent offsets inside the survey panel — NOT geographic coordinates. */
  x: number;
  y: number;
  label: string;
  simulated: true;
}

export interface DemoMission {
  id: string;
  name: string;
  vessel: string;
  survey: string;
  /** Drop a bundled sonar frame here to enable one-click demo analysis. */
  sampleImageUrl: string | null;
  /** Track polyline points (percent space) for the survey visual. */
  track: Array<{ x: number; y: number }>;
  markers: DemoMarker[];
}

export const DEMO_MISSION: DemoMission = {
  id: "DEMO-001",
  name: "Demo Mission — Coastal Survey",
  vessel: "Survey Launch (simulated)",
  survey: "Side-scan lane pattern (simulated)",
  sampleImageUrl: null,
  track: [
    { x: 8, y: 18 },
    { x: 88, y: 24 },
    { x: 88, y: 44 },
    { x: 10, y: 50 },
    { x: 10, y: 70 },
    { x: 88, y: 78 },
  ],
  markers: [
    { x: 34, y: 22, label: "Contact A", simulated: true },
    { x: 66, y: 47, label: "Contact B", simulated: true },
    { x: 24, y: 74, label: "Contact C", simulated: true },
  ],
};

export const DEMO_DISCLAIMER =
  "DEMO / SIMULATED LOCATION — no real navigation data. Positions appear once XTF/JSF navigation parsing is connected.";
