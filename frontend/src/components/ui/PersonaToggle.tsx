"use client";

import { UserRound, Stethoscope } from "lucide-react";
import { usePersona } from "@/lib/persona";
import { cn } from "@/lib/utils";

interface PersonaToggleProps {
  /** `compact` hides labels — used in the mobile header. */
  compact?: boolean;
  className?: string;
}

export function PersonaToggle({ compact = false, className }: PersonaToggleProps) {
  const { persona, setPersona } = usePersona();

  const options = [
    { value: "patient" as const, label: "Patient", icon: UserRound },
    { value: "clinician" as const, label: "Clinician", icon: Stethoscope },
  ];

  return (
    <div
      role="radiogroup"
      aria-label="View mode"
      className={cn(
        "flex items-center gap-1 p-1 rounded-full bg-neutral-100 dark:bg-neutral-800",
        className
      )}
    >
      {options.map((option) => {
        const Icon = option.icon;
        const active = persona === option.value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => setPersona(option.value)}
            title={`${option.label} view`}
            className={cn(
              "flex items-center gap-1.5 rounded-full transition-colors",
              compact ? "px-2 py-1.5" : "px-3 py-1.5",
              active
                ? "bg-white dark:bg-neutral-700 text-primary-700 dark:text-primary-300 shadow-sm"
                : "text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200"
            )}
          >
            <Icon size={14} className="shrink-0" />
            {compact && <span className="sr-only">{option.label} view</span>}
            {!compact && (
              <span className="text-xs font-medium">{option.label}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
