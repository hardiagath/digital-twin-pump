"use client";
import Plot from "./Plot";
import { useThemeColors } from "./useThemeColors";
import { AnomalyTrendPoint } from "@/lib/types";
import { RISK_HEX } from "@/lib/utils";
import { formatHour } from "@/lib/utils";

export default function AnomalyTrendChart({ data }: { data: AnomalyTrendPoint[] }) {
  const colors = useThemeColors();
  const x = data.map((d) => formatHour(d.timestamp));
  const y = data.map((d) => d.anomaly_score);
  const markerColors = data.map((d) => RISK_HEX[d.risk_level] ?? colors.muted);

  return (
    <div className="card p-4">
      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
        Anomaly Score History
      </p>
      <Plot
        data={[
          {
            x,
            y,
            type: "scatter",
            mode: "lines+markers",
            line: { color: colors.grid, width: 1.5 },
            marker: { color: markerColors, size: 6 },
            hovertemplate: "%{y:.2f}<extra></extra>",
          },
        ]}
        layout={{
          autosize: true,
          height: 260,
          margin: { l: 40, r: 12, t: 10, b: 32 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { color: colors.muted, size: 10 },
          xaxis: { showgrid: false, tickfont: { size: 9 } },
          yaxis: {
            gridcolor: colors.grid,
            zeroline: false,
            range: [0, 1],
            tickfont: { size: 9 },
          },
          shapes: [
            {
              type: "line",
              x0: 0, x1: 1, xref: "paper",
              y0: 0.3, y1: 0.3,
              line: { color: RISK_HEX.warning, width: 1, dash: "dot" },
            },
            {
              type: "line",
              x0: 0, x1: 1, xref: "paper",
              y0: 0.6, y1: 0.6,
              line: { color: RISK_HEX.critical, width: 1, dash: "dot" },
            },
          ],
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%" }}
        useResizeHandler
      />
    </div>
  );
}
