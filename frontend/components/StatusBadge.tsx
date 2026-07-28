import { riskBadge, RiskLevel } from "@/lib/utils";

export default function StatusBadge({ level }: { level: RiskLevel }) {
  return <span className={riskBadge(level)}>{level}</span>;
}