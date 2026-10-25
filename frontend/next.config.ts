import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Emits .next/standalone — a self-contained server used by the
  // container image (see frontend/Dockerfile).
  output: "standalone",
  turbopack: {
    root: path.resolve(__dirname),
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
