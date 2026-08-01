"use client";
import { Alert } from "@/lib/types";
import { riskBadge, formatTimestamp, RiskLevel } from "@/lib/utils";
import { resolveAlert, getRecommendation } from "@/lib/api";
import { useState } from "react";
import { CheckCircle, ChevronDown, ChevronUp } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function AlertCard({
  alert,
  onResolved,
}: {
  alert:      Alert;
  onResolved: () => void;
}) {
  const [expanded,       setExpanded]       = useState(false);
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [loadingRec,     setLoadingRec]     = useState(false);
  const [resolving,      setResolving]      = useState(false);

  const handleExpand = async () => {
    setExpanded((p) => !p);
    if (!recommendation && !expanded) {
      setLoadingRec(true);
      try {
        const data = await getRecommendation(alert.id);
        setRecommendation(data.recommendation);
      } catch {
        setRecommendation("Could not load recommendation.");
      } finally {
        setLoadingRec(false);
      }
    }
  };

  const handleResolve = async () => {
    setResolving(true);
    try {
      await resolveAlert(alert.id);
      onResolved();
    } finally {
      setResolving(false);
    }
  };

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className={riskBadge(alert.risk_level as RiskLevel)}>
              {alert.risk_level}
            </span>
            <span className="text-sm font-semibold capitalize text-foreground">
              {alert.pump_part}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">{alert.message}</p>
          <p className="text-xs text-muted-foreground/70">{formatTimestamp(alert.created_at)}</p>
        </div>

        <div className="flex gap-2 shrink-0">
          <button
            onClick={handleResolve}
            disabled={resolving}
            className="text-risk-normal hover:opacity-80 transition-opacity disabled:opacity-40"
            title="Resolve alert"
          >
            <CheckCircle size={18} />
          </button>
          <button
            onClick={handleExpand}
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="View recommendation"
          >
            {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="bg-surface-hover rounded-2xl p-3 text-sm text-foreground/90 leading-relaxed">
          {loadingRec ? (
            <p className="text-muted-foreground italic">Loading AI recommendation...</p>
          ) : (
            <ReactMarkdown
              components={{
                h1: (props) => <p className="font-semibold mb-1" {...props} />,
                h2: (props) => <p className="font-semibold mb-1" {...props} />,
                h3: (props) => <p className="font-semibold mb-1" {...props} />,
                p:  (props) => <p className="mb-2 last:mb-0" {...props} />,
                strong: (props) => <strong className="font-semibold text-foreground" {...props} />,
                ul: (props) => <ul className="list-disc pl-4 mb-2 space-y-0.5" {...props} />,
                ol: (props) => <ol className="list-decimal pl-4 mb-2 space-y-0.5" {...props} />,
                li: (props) => <li {...props} />,
              }}
            >
              { }
              {(recommendation ?? "").replace(/\\n/g, "\n")}
            </ReactMarkdown>
          )}
        </div>
      )}
    </div>
  );
}