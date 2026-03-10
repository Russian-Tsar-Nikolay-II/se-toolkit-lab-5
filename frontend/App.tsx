import { useState } from 'react'
import Dashboard from './Dashboard'

export default function App(): JSX.Element {
  const [page, setPage] = useState<'items' | 'dashboard'>('dashboard')

  return (
    <div>
      <nav>
        <button onClick={() => setPage('items')}>Items</button>
        <button onClick={() => setPage('dashboard')}>Dashboard</button>
      </nav>
      {page === 'dashboard' ? <Dashboard /> : <div>Items Page</div>}
    </div>
  )
}