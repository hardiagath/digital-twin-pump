"use client";
import Plot from "./Plot";
import { useThemeColors } from "./useThemeColors";
import { RISK_HEX } from "@/lib/utils";

export default function RiskDistributionChart({
  distribution,
}: {
  distribution: { normal?: number; warning?: number; critical?: number };
}) {
  const colors = useThemeColors();
  const labels = ["Normal", "Warning", "Critical"];
  const values = [
    distribution.normal ?? 0,
    distribution.warning ?? 0,
    distribution.critical ?? 0,
  ];
  const markerColors = [RISK_HEX.normal, RISK_HEX.warning, RISK_HEX.critical];
  const total = values.reduce((a, b) => a + b, 0);

  return (
    <div className="card p-4">
      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
        Risk Distribution
      </p>
      {total === 0 ? (
        <div className="h-[260px] flex items-center justify-center">
          <p className="text-sm text-muted-foreground">No readings in this window</p>
        </div>
      ) : (
        <Plot
          data={[
            {
              labels,
              values,
              type: "pie",
              hole: 0.62,
              marker: { colors: markerColors },
              textinfo: "none",
              hovertemplate: "%{label}: %{value} (%{percent})<extra></extra>",
            },
          ]}
          layout={{
            autosize: true,
            height: 260,
            margin: { l: 10, r: 10, t: 10, b: 10 },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            font: { color: colors.text, size: 11 },
            showlegend: true,
            legend: { orientation: "h", y: -0.05, font: { size: 10 } },
          }}
          config={{ displayModeBar: false, responsive: true }}
          style={{ width: "100%" }}
          useResizeHandler
        />
      )}
    </div>
  );
}
