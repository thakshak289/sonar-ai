import { useCallback, useEffect, useState } from "react";

import { checkBackendHealth } from "@/lib/sonar-api";

export type BackendStatus = "checking" | "online" | "offline";

/** Probes the FastAPI AI engine so the UI can show a truthful status. */
export function useBackendStatus(pollMs = 30000) {
  const [status, setStatus] = useState<BackendStatus>("checking");

  const refresh = useCallback(async () => {
    const ok = await checkBackendHealth();
    setStatus(ok ? "online" : "offline");
  }, []);

  useEffect(() => {
    let active = true;
    const run = async () => {
      const ok = await checkBackendHealth();
      if (active) setStatus(ok ? "online" : "offline");
    };
    run();
    const id = setInterval(run, pollMs);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [pollMs]);

  return { status, refresh };
}
