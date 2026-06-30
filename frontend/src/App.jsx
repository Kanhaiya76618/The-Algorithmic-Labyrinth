// SHARED shell — frozen after Day 1. Just the layout + route outlet.
import { Outlet, Link } from "react-router-dom";

export default function App() {
  return (
    <div className="shell">
      <nav className="topbar">
        <Link to="/">Dungeon</Link>
        <Link to="/memory/demo">Memory</Link>
      </nav>
      <Outlet />
    </div>
  );
}
