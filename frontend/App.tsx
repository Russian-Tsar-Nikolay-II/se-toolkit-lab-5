cat > src/App.tsx << 'EOF'
import { useState } from 'react'
import Dashboard from './Dashboard'

export default function App(): JSX.Element {
  const [currentPage, setCurrentPage] = useState<'items' | 'dashboard'>('dashboard')

  return (
    <div className="min-h-screen">
      <nav className="p-4 bg-gray-800 text-white flex gap-4">
        <button
          onClick={() => setCurrentPage('items')}
          className={`px-4 py-2 rounded ${currentPage === 'items' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
        >
          Items
        </button>
        <button
          onClick={() => setCurrentPage('dashboard')}
          className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
        >
          Dashboard
        </button>
      </nav>
      <main>
        {currentPage === 'dashboard' ? <Dashboard /> : <div className="p-4">Items Page</div>}
      </main>
    </div>
  )
}
EOF