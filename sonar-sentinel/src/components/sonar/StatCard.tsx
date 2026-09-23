import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Tone = "default" | "ok" | "warn" | "danger" | "primary";

const valueTone: Record<Tone, string> = {
  default: "text-foreground",
  primary: "text-primary",
  ok: "text-ok",
  warn: "text-warn",
  danger: "text-danger",
};

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: string | number;
  hint?: string;
  icon?: LucideIcon;
  tone?: Tone;
}) {
  return (
    <Card className="border-border/70 bg-surface panel-glow">
      <CardContent className="flex items-start justify-between gap-3 p-4">
        <div className="min-w-0">
          <p className="font-mono text-[11px] tracking-widest text-muted-foreground uppercase">
            {label}
          </p>
          <p className={cn("mt-2 text-2xl font-semibold tabular-nums", valueTone[tone])}>{value}</p>
          {hint && <p className="mt-1 truncate text-xs text-muted-foreground">{hint}</p>}
        </div>
        {Icon && (
          <span className="rounded-md border border-border/70 bg-surface-raised p-2 text-primary">
            <Icon className="h-4 w-4" />
          </span>
        )}
      </CardContent>
    </Card>
  );
}
