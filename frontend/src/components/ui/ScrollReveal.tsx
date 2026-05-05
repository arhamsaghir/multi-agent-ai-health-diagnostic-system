"use client";

import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { cn } from "@/lib/utils";

interface ScrollRevealProps {
  children: React.ReactNode;
  delay?: number;
  direction?: "up" | "down" | "left" | "right";
  distance?: number;
  duration?: number;
  once?: boolean;
  className?: string;
}

const directionValues = {
  up: 20,
  down: 20,
  left: 20,
  right: 20,
};

export function ScrollReveal({
  children,
  delay = 0,
  direction = "up",
  distance,
  duration = 0.4,
  once = true,
  className,
}: ScrollRevealProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once, margin: "-50px" });
  const dist = distance ?? directionValues[direction];

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: direction === "up" ? dist : direction === "down" ? -dist : 0, x: direction === "left" ? dist : direction === "right" ? -dist : 0 }}
      animate={isInView ? { opacity: 1, x: 0, y: 0 } : undefined}
      transition={{ duration, delay, ease: "easeOut" }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  );
}

interface FloatProps {
  children: React.ReactNode;
  className?: string;
}

export function Float({ children, className }: FloatProps) {
  return (
    <motion.div
      className={cn("animate-float", className)}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {children}
    </motion.div>
  );
}