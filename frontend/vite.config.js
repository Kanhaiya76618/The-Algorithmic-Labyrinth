import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/game": "http://localhost:8000",
                     "/content": "http://localhost:8000",
                     "/memory": "http://localhost:8000" } },
});
