import { useEffect, useState } from 'react';
import AgentGuard from './components/AgentGuard'
import Landing from './components/Landing'

function App() {
  const [showLanding, setShowLanding] = useState(() => !isControlHash(window.location.hash));

  useEffect(() => {
    const handleHistoryChange = () => setShowLanding(!isControlHash(window.location.hash));
    window.addEventListener('hashchange', handleHistoryChange);
    window.addEventListener('popstate', handleHistoryChange);
    return () => {
      window.removeEventListener('hashchange', handleHistoryChange);
      window.removeEventListener('popstate', handleHistoryChange);
    };
  }, []);

  const enterControl = () => {
    window.history.pushState({ mode: 'control' }, '', '#simulator');
    setShowLanding(false);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {showLanding ? (
        <Landing onComplete={enterControl} />
      ) : (
        <AgentGuard onBack={() => {
          window.history.replaceState({}, '', window.location.pathname + window.location.search);
          setShowLanding(true);
        }} />
      )}
    </div>
  )
}

function isControlHash(hash: string) {
  return hash === '#dashboard' || hash === '#simulator';
}

export default App
