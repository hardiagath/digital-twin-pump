"use client";
import { useState } from "react";
import clsx from "clsx";
import { Check, Copy, RotateCcw } from "lucide-react";
import { HotspotPosition, PumpPart } from "@/lib/types";

interface Props {
  hotspots:    HotspotPosition[];
  activePart:  PumpPart;
  onSelectPart: (part: PumpPart) => void;
  onReset:     () => void;
}

export default function HotspotCalibrator({
  hotspots,
  activePart,
  onSelectPart,
  onReset,
}: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const config = hotspots
      .map(
        (h) =>
          `  { part: "${h.part}", label: "${h.label}", position: [${h.position[0]}, ${h.position[1]}, ${h.position[2]}] },`
      )
      .join("\n");
    const snippet = `export const DEFAULT_HOTSPOTS: HotspotPosition[] = [\n${config}\n];`;

    await navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="card p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">
          Calibrating -- click the model to place
        </p>
        <button
          onClick={onReset}
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <RotateCcw size={12} /> Reset to defaults
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {hotspots.map((h) => (
          <button
            key={h.part}
            onClick={() => onSelectPart(h.part)}
            className={clsx(
              "rounded-2xl border px-3 py-2 text-left text-xs transition-colors",
              activePart === h.part
                ? "border-accent bg-accent/10"
                : "border-border hover:bg-surface-hover"
            )}
          >
            <p className="font-semibold">{h.label}</p>
            <p className="text-muted-foreground font-mono">
              {h.position.map((n) => n.toFixed(1)).join(", ")}
            </p>
          </button>
        ))}
      </div>

      <button
        onClick={handleCopy}
        className="self-start flex items-center gap-1.5 text-xs bg-surface-hover border border-border rounded-full px-3 py-1.5 hover:bg-border/40 transition-colors"
      >
        {copied ? <Check size={12} /> : <Copy size={12} />}
        {copied ? "Copied!" : "Copy config for lib/hotspots.ts"}
      </button>
      <p className="text-xs text-muted-foreground">
        This only changes what you see right now -- nothing is saved until you paste
        the copied snippet into <code className="font-mono">lib/hotspots.ts</code> yourself.
        Refresh the page any time to undo.
      </p>
    </div>
  );
}
