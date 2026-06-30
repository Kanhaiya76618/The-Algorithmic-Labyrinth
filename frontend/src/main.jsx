// SHARED — set up ONCE on Day 1, then frozen.
// Routes are declared up front; each page already exists as a stub so the
// app boots. After today, each role edits only their own page file.
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App.jsx";
import DungeonPage from "./pages/DungeonPage.jsx";
import BossPage from "./pages/BossPage.jsx";
import MemoryView from "./pages/MemoryView.jsx";
import "./styles/theme.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route element={<App />}>
        <Route index element={<DungeonPage />} />
        <Route path="boss" element={<BossPage />} />
        <Route path="memory/:playerId" element={<MemoryView />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
