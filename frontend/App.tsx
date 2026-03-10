import { useState } from 'react'
import Dashboard from './Dashboard'

export default function App() {
  const [page, setPage] = useState<'items' | 'dashboard'>('dashboard')

  return (
    <div>
      <nav className="p-4 bg-gray-800 text-white flex gap-4">
        <button onClick={() => setPage('items')} className="px-3 py-1">Items</button>
        <button onClick={() => setPage('dashboard')} className="px-3 py-1">Dashboard</button>
      </nav>
      {page === 'dashboard' ? <Dashboard /> : <div className="p-4">Items</div>}
    </div>
  )
}