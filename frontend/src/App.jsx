import { Routes, Route, Navigate } from 'react-router-dom'
import DungeonPage from './pages/DungeonPage.jsx'
import BossPage from './pages/BossPage.jsx'
import MemoryView from './pages/MemoryView.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DungeonPage />} />
      <Route path="/boss" element={<BossPage />} />
      <Route path="/memory" element={<MemoryView />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
