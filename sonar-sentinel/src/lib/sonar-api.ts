/**
 * Backend contract for the SONAR-AI FastAPI service.
 *
 * No detection logic lives in the frontend. Everything rendered as a real
 * detection comes from the backend response.
 */

export const BACKEND_URL: string = (
  (import.meta.env["VITE_SONAR_API_URL"] as string | undefined) ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export type RiskLevel = "high" | "medium" | "low" | string;

export interface Detection {
  label: string;
  confidence: number;
  risk: RiskLevel;
  box: [number, number, number, number];
}

export interface AnalysisSummary {
  total_targets: number;
  high_risk_targets: number;
  processing_time: number;
}

export interface ImageAnalysisResponse {
  success: boolean;
  filename: string;
  image: { width: number; height: number };
  detections: Detection[];
  summary: AnalysisSummary;
  annotated_image?: string | null;
  error?: string;
}

/** Result source, so the UI can never present demo data as a real model output. */
export type ResultSource = "backend" | "demo";

export interface AnalysisResult {
  source: ResultSource;
  data: ImageAnalysisResponse;
}

export class BackendUnavailableError extends Error {
  constructor(message = "AI backend unreachable") {
    super(message);
    this.name = "BackendUnavailableError";
  }
}

/** Resolves relative annotated-image paths against the backend origin. */
export function resolveAssetUrl(src?: string | null): string | null {
  if (!src) return null;
  if (/^(https?:|data:|blob:)/i.test(src)) return src;
  return `${BACKEND_URL}/${src.replace(/^\/+/, "")}`;
}

export function averageConfidence(detections: Detection[]): number {
  if (detections.length === 0) return 0;
  return detections.reduce((sum, d) => sum + d.confidence, 0) / detections.length;
}

/** Normalises confidence that may arrive as 0-1 or 0-100. */
export function confidencePercent(confidence: number): number {
  const pct = confidence <= 1 ? confidence * 100 : confidence;
  return Math.max(0, Math.min(100, pct));
}

async function ping(path: string, timeoutMs = 4000): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BACKEND_URL}${path}`, { signal: controller.signal });
    return res.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

/** Best-effort health probe; tries /health then falls back to the root. */
export async function checkBackendHealth(): Promise<boolean> {
  if (await ping("/health")) return true;
  return ping("/");
}

export async function analyzeSonarImage(file: File): Promise<ImageAnalysisResponse> {
  const body = new FormData();
  body.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}/api/analyze/image`, { method: "POST", body });
  } catch {
    throw new BackendUnavailableError(
      `Could not reach the AI engine at ${BACKEND_URL}. Start the FastAPI service and try again.`,
    );
  }

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      `Analysis failed (${response.status}). ${text.slice(0, 300) || "The AI engine returned an error."}`,
    );
  }

  const data = (await response.json()) as ImageAnalysisResponse;
  if (!data || data.success === false) {
    throw new Error(data?.error || "The AI engine reported an unsuccessful analysis.");
  }
  return {
    ...data,
    detections: data.detections ?? [],
    summary: data.summary ?? { total_targets: 0, high_risk_targets: 0, processing_time: 0 },
  };
}
