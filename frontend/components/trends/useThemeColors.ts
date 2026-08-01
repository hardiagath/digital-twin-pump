"use client";
import { useEffect, useState } from "react";
import { useTheme } from "next-themes";

export interface ThemeColors {
  text:  string;
  muted: string;
  grid:  string;
}

const FALLBACK: ThemeColors = { text: "#9a9d8f", muted: "#9a9d8f", grid: "#232519" };

export function useThemeColors(): ThemeColors {
  const { resolvedTheme } = useTheme();
  const [colors, setColors] = useState<ThemeColors>(FALLBACK);

  useEffect(() => {
    if (typeof window === "undefined") return;
    Promise.resolve().then(() => {
      const styles = getComputedStyle(document.documentElement);
      setColors({
        text:  styles.getPropertyValue("--foreground").trim()        || FALLBACK.text,
        muted: styles.getPropertyValue("--muted-foreground").trim()  || FALLBACK.muted,
        grid:  styles.getPropertyValue("--chart-grid").trim()        || FALLBACK.grid,
      });
    });
  }, [resolvedTheme]);

  return colors;
}
