import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";
import fs from "fs";

const buildVersion = `${Date.now()}`;

export default defineConfig({
  plugins: [
    vue(),
    {
      name: "generate-version-file",
      writeBundle() {
        const outDir = path.resolve(__dirname, "../pollcast/public/frontend");
        if (!fs.existsSync(outDir)) {
          fs.mkdirSync(outDir, { recursive: true });
        }
        fs.writeFileSync(
          path.resolve(outDir, "version.json"),
          JSON.stringify(
            {
              version: buildVersion,
              build_time: new Date().toISOString(),
            },
            null,
            2,
          ),
        );
      },
    },
  ],

  define: {
    __APP_BUILD_VERSION__: JSON.stringify(buildVersion),
  },

  // Base URL for assets served from Frappe
  base: "/assets/pollcast/frontend/",

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  // Dev server: proxy API/asset calls to local Frappe bench
  server: {
    proxy: {
      "/api":    { target: "http://localhost:8000", changeOrigin: true },
      "/assets": { target: "http://localhost:8000", changeOrigin: true },
      "/files":  { target: "http://localhost:8000", changeOrigin: true },
    },
  },

  build: {
    // Output to Frappe's public directory so it's served as a static asset
    outDir: "../pollcast/public/frontend",
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        // Fixed filenames so pollcast.html can reference them directly
        entryFileNames: "index.js",
        chunkFileNames: "[name]-[hash].js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith(".css")) {
            return "index.css";
          }
          return "[name]-[hash][extname]";
        },
      },
    },
  },
});
