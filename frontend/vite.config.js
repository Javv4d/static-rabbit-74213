import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./", // Use relative paths for both local and GitHub Pages
  build: {
    outDir: "dist",
    assetsDir: "assets",
  },
  server: {
    port: 5173
  }
});
