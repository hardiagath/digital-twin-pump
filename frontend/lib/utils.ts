import clsx from "clsx";

export type RiskLevel = "normal" | "warning" | "critical";

export const RISK_HEX: Record<RiskLevel, string> = {
  normal:   "#4ade80",
  warning:  "#fbbf24",
  critical: "#f87171",
};

export const riskColor = (level: RiskLevel) =>
  clsx({
    "text-risk-normal":   level === "normal",
    "text-risk-warning":  level === "warning",
    "text-risk-critical": level === "critical",
  });

export const riskBg = (level: RiskLevel) =>
  clsx("border", {
    "bg-risk-normal/10 border-risk-normal/30":     level === "normal",
    "bg-risk-warning/10 border-risk-warning/30":   level === "warning",
    "bg-risk-critical/10 border-risk-critical/30": level === "critical",
  });

export const riskBadge = (level: RiskLevel) =>
  clsx(
    "px-2 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wide",
    {
      "bg-risk-normal/15 text-risk-normal":     level === "normal",
      "bg-risk-warning/15 text-risk-warning":   level === "warning",
      "bg-risk-critical/15 text-risk-critical": level === "critical",
    }
  );

export const riskDot = (level: RiskLevel) =>
  clsx("rounded-full", {
    "bg-risk-normal":   level === "normal",
    "bg-risk-warning":  level === "warning",
    "bg-risk-critical": level === "critical",
  });

export const formatTimestamp = (ts: string) =>
  new Date(ts).toLocaleString("en-IN", {
    day:    "2-digit",
    month:  "short",
    hour:   "2-digit",
    minute: "2-digit",
  });

export const formatHour = (ts: string) =>
  new Date(ts.replace(" ", "T")).toLocaleString("en-IN", {
    day:   "2-digit",
    month: "short",
    hour:  "2-digit",
  });
