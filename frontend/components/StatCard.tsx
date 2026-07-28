import { riskBg, RiskLevel } from "@/lib/utils";
import clsx from "clsx";

interface Props {
  title:     string;
  value:     string | number;
  unit?:     string;
  risk?:     RiskLevel;
  subtitle?: string;
}

export default function StatCard({ title, value, unit, risk = "normal", subtitle }: Props) {
  return (
    <div className={clsx("rounded-xl p-4 flex flex-col gap-1", riskBg(risk))}>
      <p className="text-xs text-gray-400 uppercase tracking-wider">{title}</p>
      <p className="text-2xl font-bold text-white">
        {value}
        {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
      </p>
      {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
}