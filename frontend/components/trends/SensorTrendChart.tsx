"use client";
import Plot from "./Plot";
import { useThemeColors } from "./useThemeColors";
import { SensorTrendPoint } from "@/lib/types";
import { formatHour } from "@/lib/utils";

const SENSORS: { key: keyof SensorTrendPoint; label: string; unit: string }[] = [
  { key: "temperature", label: "Temperature", unit: "°C" },
  { key: "vibration",   label: "Vibration",   unit: "mm/s" },
  { key: "pressure",    label: "Pressure",    unit: "bar" },
  { key: "rpm",         label: "RPM",         unit: "rpm" },
  { key: "flow_rate",   label: "Flow Rate",   unit: "m³/h" },
];

export default function SensorTrendChart({ data }: { data: SensorTrendPoint[] }) {
  const colors = useThemeColors();
  const x = data.map((d) => formatHour(d.timestamp));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {SENSORS.map((sensor) => (
        <div key={sensor.key} className="card p-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            {sensor.label}
          </p>
          <Plot
            data={[
              {
                x,
                y: data.map((d) => d[sensor.key] as number),
                type: "scatter",
                mode: "lines",
                line: { color: colors.text, width: 2, shape: "spline" },
                fill: "tozeroy",
                fillcolor: "rgba(150,160,140,0.08)",
                hovertemplate: `%{y} ${sensor.unit}<extra></extra>`,
              },
            ]}
            layout={{
              autosize: true,
              height: 180,
              margin: { l: 36, r: 12, t: 8, b: 28 },
              paper_bgcolor: "rgba(0,0,0,0)",
              plot_bgcolor: "rgba(0,0,0,0)",
              font: { color: colors.muted, size: 10 },
              xaxis: { showgrid: false, tickfont: { size: 9 } },
              yaxis: { gridcolor: colors.grid, zeroline: false, tickfont: { size: 9 } },
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: "100%" }}
            useResizeHandler
          />
        </div>
      ))}
    </div>
  );
}
