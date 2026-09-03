import { useState, useEffect } from "react";
import { Activity, History, Shield, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Dashboard from "./Dashboard";
import Simulator from "./Simulator";
import Mascot from "./Mascot";

export default function AgentGuard() {
  const [activeTab, setActiveTab] = useState(window.location.hash.replace('#', '') || "simulator");

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash) setActiveTab(hash);
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const changeTab = (tab: string) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#050505] text-white font-sans selection:bg-[#00f0ff] selection:text-black">
      {/* Decorative Grid Background */}
      <div className="absolute inset-0 pointer-events-none opacity-20" style={{ backgroundImage: 'radial-gradient(rgba(0, 240, 255, 0.3) 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
      
      {/* Sidebar - Deep Tech Glass */}
      <div className="w-72 glass-panel m-4 flex flex-col z-20 overflow-hidden shadow-[0_0_40px_rgba(0,240,255,0.05)] border-l-4 border-l-[#00f0ff]">
        <div className="px-8 py-8 border-b border-white/10 bg-black/20">
          <h1 className="text-2xl font-bold flex items-center gap-3 tracking-tight text-white">
            <Shield className="text-[#00f0ff]" size={28} strokeWidth={2} />
            AGENT<span className="font-light text-white/50">GUARD</span>
          </h1>
          <p className="neon-text-blue font-mono text-[10px] tracking-widest uppercase mt-3 py-1">
            Risk Controller v2.0
          </p>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 mt-2">
          <NavButton active={activeTab === 'dashboard'} onClick={() => changeTab("dashboard")} icon={<Activity size={18} />} text="DASHBOARD" />
          <NavButton active={activeTab === 'simulator'} onClick={() => changeTab("simulator")} icon={<History size={18} />} text="SIMULATOR" />
        </nav>
        
        <div className="p-6 border-t border-white/10 bg-black/20">
          <div className="flex items-center gap-3">
            <motion.div animate={{ opacity: [1, 0.3, 1] }} transition={{ duration: 2, repeat: Infinity }}>
              <Zap size={20} className="text-[#39ff14]" />
            </motion.div>
            <p className="font-mono text-sm tracking-wide text-white/60">
              System <span className="neon-text-green">Live</span>
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="px-12 py-8 flex justify-between items-center z-10">
          <motion.h2 
            key={activeTab}
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="text-3xl font-light tracking-wider uppercase text-white/90"
          >
            {activeTab}
          </motion.h2>
          <div className="flex items-center">
            <span className="font-mono text-xs px-3 py-1 rounded-full border border-[#b026ff] text-[#b026ff] shadow-[0_0_10px_rgba(176,38,255,0.2)]">
              Sandbox Env
            </span>
          </div>
        </header>
        
        <main className="flex-1 overflow-auto px-12 pb-12 z-10 scrollbar-hide relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.3 }}
              className="h-full max-w-7xl mx-auto"
            >
              {activeTab === 'dashboard' && <Dashboard />}
              {activeTab === 'simulator' && <Simulator />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
      
      {/* Sentient Orb Mascot */}
      <Mascot />
    </div>
  );
}

function NavButton({ active, onClick, icon, text }: any) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all font-mono tracking-wider text-sm ${
        active 
          ? 'bg-[#00f0ff]/10 text-[#00f0ff] border border-[#00f0ff]/30 shadow-[0_0_15px_rgba(0,240,255,0.1)]' 
          : 'text-white/50 hover:bg-white/5 hover:text-white/90 border border-transparent'
      }`}
    >
      {icon}
      <span>{text}</span>
    </button>
  );
}
