import { useState } from 'react';
import AgentGuard from './components/AgentGuard'
import Landing from './components/Landing'

function App() {
  const [showLanding, setShowLanding] = useState(true);

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {showLanding ? (
        <Landing onComplete={() => setShowLanding(false)} />
      ) : (
        <AgentGuard />
      )}
    </div>
  )
}

export default App
