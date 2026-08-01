import { riskColor, RiskLevel } from "@/lib/utils";
import clsx from "clsx";

interface Props {
  title:     string;
  value:     string | number;
  unit?:     string;
  risk?:     RiskLevel;
  subtitle?: string;
}

export default function StatCard({ title, value, unit, risk, subtitle }: Props) {
  return (
    <div className="card p-5 flex flex-col gap-2">
      <p className="text-xs text-muted-foreground uppercase tracking-wider">{title}</p>
      <p
        className={clsx(
          "text-3xl font-medium tracking-tight",
          risk ? riskColor(risk) : "text-foreground"
        )}
      >
        {value}
        {unit && (
          <span className="text-sm font-normal text-muted-foreground ml-1.5">{unit}</span>
        )}
      </p>
      {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
    </div>
  );
}
