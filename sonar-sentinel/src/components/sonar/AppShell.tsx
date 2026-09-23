import { Link, useRouterState } from "@tanstack/react-router";
import {
  FileText,
  Image as ImageIcon,
  LayoutDashboard,
  Map as MapIcon,
  Menu,
  Radar,
  Radio,
  Waves,
  X,
} from "lucide-react";
import { useState } from "react";

import { StatusPill } from "@/components/sonar/StatusPill";
import { Button } from "@/components/ui/button";
import { useBackendStatus } from "@/hooks/use-backend-status";
import { BACKEND_URL } from "@/lib/sonar-api";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/image-analysis", label: "Image Analysis", icon: ImageIcon },
  { to: "/mission-analysis", label: "Mission Analysis", icon: Waves },
  { to: "/mission-map", label: "Mission Map", icon: MapIcon },
  { to: "/reports", label: "Reports", icon: FileText },
] as const;

function Brand() {
  return (
    <Link to="/" className="flex items-center gap-2.5">
      <span className="rounded-md border border-primary/30 bg-primary/10 p-1.5 text-primary">
        <Radar className="h-5 w-5" />
      </span>
      <span className="leading-tight">
        <span className="block font-mono text-sm font-bold tracking-[0.18em] text-foreground">
          SONAR-AI
        </span>
        <span className="block text-[10px] tracking-wide text-muted-foreground">
          Marine Debris Intelligence
        </span>
      </span>
    </Link>
  );
}

function NavList({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <nav className="space-y-1">
      {NAV.map(({ to, label, icon: Icon }) => {
        const active = pathname === to;
        return (
          <Link
            key={to}
            to={to}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
              active
                ? "bg-sidebar-accent text-sidebar-accent-foreground border border-primary/25"
                : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-foreground border border-transparent",
            )}
          >
            <Icon className={cn("h-4 w-4", active && "text-primary")} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

function EngineFooter() {
  return (
    <div className="rounded-lg border border-border/70 bg-surface p-3">
      <p className="font-mono text-[10px] tracking-widest text-muted-foreground uppercase">
        model
      </p>
      <p className="mt-1 text-xs font-semibold">GhostVision YOLO26 · ONNX</p>
      <p className="mt-1 text-[11px] text-muted-foreground">
        Current class: Crab-Pot (derelict fishing gear)
      </p>
      <p className="mt-2 font-mono text-[10px] break-all text-muted-foreground">{BACKEND_URL}</p>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const { status } = useBackendStatus();

  const engine =
    status === "online"
      ? { tone: "ok" as const, text: "AI Engine Online" }
      : status === "checking"
        ? { tone: "muted" as const, text: "Contacting Engine" }
        : { tone: "danger" as const, text: "AI Engine Offline" };

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col justify-between border-r border-sidebar-border bg-sidebar p-4 lg:flex">
        <div className="space-y-6">
          <Brand />
          <NavList />
        </div>
        <EngineFooter />
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-background/80" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 flex w-72 flex-col justify-between border-r border-sidebar-border bg-sidebar p-4">
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <Brand />
                <Button variant="ghost" size="icon" onClick={() => setOpen(false)} aria-label="Close menu">
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <NavList onNavigate={() => setOpen(false)} />
            </div>
            <EngineFooter />
          </aside>
        </div>
      )}

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-border/70 bg-background/85 px-4 py-3 backdrop-blur">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="lg:hidden">
            <Brand />
          </div>

          <div className="ml-auto flex items-center gap-2">
            <StatusPill tone={engine.tone} pulse={status === "online"}>
              {engine.text}
            </StatusPill>
            <Button asChild variant="outline" size="sm" className="border-primary/30 text-primary">
              <Link to="/mission-map">
                <Radio className="mr-1.5 h-3.5 w-3.5" />
                Demo Mission
              </Link>
            </Button>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:py-8">{children}</main>

        <footer className="border-t border-border/70 px-4 py-5 text-center text-xs text-muted-foreground sm:px-6">
          SONAR-AI · SIH prototype · Current AI prototype: derelict fishing-gear detection from
          side-scan sonar imagery.
        </footer>
      </div>
    </div>
  );
}
