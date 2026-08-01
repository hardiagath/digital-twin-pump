"use client";
import clsx from "clsx";

const RANGES = [
  { label: "6h",  hours: 6 },
  { label: "24h", hours: 24 },
  { label: "7d",  hours: 168 },
];

export default function TimeRangeSelector({
  value,
  onChange,
}: {
  value:    number;
  onChange: (hours: number) => void;
}) {
  return (
    <div className="pill inline-flex p-1 gap-1">
      {RANGES.map((r) => (
        <button
          key={r.hours}
          onClick={() => onChange(r.hours)}
          className={clsx(
            "px-3 py-1.5 rounded-full text-sm transition-colors",
            value === r.hours
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {r.label}
        </button>
      ))}
    </div>
  );
}
