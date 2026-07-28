"use client";
import { Alert } from "@/lib/types";
import { riskBadge, formatTimestamp, RiskLevel } from "@/lib/utils";
import { resolveAlert, getRecommendation } from "@/lib/api";
import { useState } from "react";
import { CheckCircle, ChevronDown, ChevronUp } from "lucide-react";

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
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <span className={riskBadge(alert.risk_level as RiskLevel)}>
              {alert.risk_level}
            </span>
            <span className="text-sm font-semibold capitalize text-white">
              {alert.pump_part}
            </span>
          </div>
          <p className="text-sm text-gray-400">{alert.message}</p>
          <p className="text-xs text-gray-600">{formatTimestamp(alert.created_at)}</p>
        </div>

        <div className="flex gap-2 shrink-0">
          <button
            onClick={handleResolve}
            disabled={resolving}
            className="text-green-400 hover:text-green-300 transition-colors"
            title="Resolve alert"
          >
            <CheckCircle size={18} />
          </button>
          <button
            onClick={handleExpand}
            className="text-gray-400 hover:text-gray-200 transition-colors"
            title="View recommendation"
          >
            {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
          {loadingRec ? (
            <p className="text-gray-500 italic">Loading AI recommendation...</p>
          ) : (
            <p className="whitespace-pre-wrap">{recommendation}</p>
          )}
        </div>
      )}
    </div>
  );
}