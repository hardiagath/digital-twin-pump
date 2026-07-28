import clsx from "clsx";

export type RiskLevel = "normal" | "warning" | "critical";

export const riskColor = (level: RiskLevel) =>
  clsx({
    "text-green-400":  level === "normal",
    "text-yellow-400": level === "warning",
    "text-red-400":    level === "critical",
  });

export const riskBg = (level: RiskLevel) =>
  clsx({
    "bg-green-400/10 border border-green-400/30":   level === "normal",
    "bg-yellow-400/10 border border-yellow-400/30": level === "warning",
    "bg-red-400/10 border border-red-400/30":       level === "critical",
  });

export const riskBadge = (level: RiskLevel) =>
  clsx(
    "px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide",
    {
      "bg-green-400/20 text-green-400":   level === "normal",
      "bg-yellow-400/20 text-yellow-400": level === "warning",
      "bg-red-400/20 text-red-400":       level === "critical",
    }
  );

export const formatTimestamp = (ts: string) =>
  new Date(ts).toLocaleString("en-IN", {
    day:    "2-digit",
    month:  "short",
    hour:   "2-digit",
    minute: "2-digit",
  });