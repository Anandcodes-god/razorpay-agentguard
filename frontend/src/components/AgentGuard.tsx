import { useState } from "react";
import { Activity, ShieldAlert, History, Shield, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Dashboard from "./Dashboard";
import Simulator from "./Simulator";

export default function AgentGuard() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="flex h-screen overflow-hidden bg-[#F4F4F0] text-black font-sans">
      {/* Sidebar - Brutalist Solid */}
      <div className="w-72 bg-[#FFD600] flex flex-col z-20 border-r-4 border-black">
        <div className="px-8 py-8 border-b-4 border-black bg-white">
          <h1 className="text-3xl font-bold font-['Space_Grotesk'] flex items-center gap-3 tracking-tight">
            <Shield className="text-black" size={32} strokeWidth={2.5} />
            AGENTGUARD
          </h1>
          <p className="text-black font-bold text-[10px] tracking-widest uppercase mt-3 py-1 px-2 border-2 border-black inline-block bg-[#FF90E8]">
            Risk Controller
          </p>
        </div>
        
        <nav className="flex-1 p-6 space-y-4 mt-2">
          <NavButton active={activeTab === 'dashboard'} onClick={() => setActiveTab("dashboard")} icon={<Activity strokeWidth={2.5} size={20} />} text="DASHBOARD" />
          <NavButton active={activeTab === 'simulator'} onClick={() => setActiveTab("simulator")} icon={<History strokeWidth={2.5} size={20} />} text="SIMULATOR" />
        </nav>
        
        <div className="p-6 border-t-4 border-black bg-[#4ADE80]">
          <div className="flex items-center gap-3">
            <Zap size={24} strokeWidth={2.5} />
            <p className="font-['Space_Grotesk'] font-bold text-sm tracking-wide uppercase">
              System Live
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden relative bg-[#F4F4F0] backgroundImagePattern">
        {/* Decorative Grid Background - achieved via tailwind utilities or inline style */}
        <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>

        <header className="px-12 py-8 flex justify-between items-center z-10 border-b-4 border-black bg-white">
          <motion.h2 
            key={activeTab}
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="text-4xl font-black font-['Space_Grotesk'] uppercase tracking-tight"
          >
            {activeTab}
          </motion.h2>
          <div className="flex items-center">
            <span className="font-['Space_Grotesk'] font-bold text-sm px-4 py-2 border-2 border-black bg-[#FF90E8] shadow-[4px_4px_0_0_rgba(0,0,0,1)] uppercase tracking-wide">
              Environment: Sandbox
            </span>
          </div>
        </header>
        
        <main className="flex-1 overflow-auto p-12 z-10 scrollbar-hide relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="h-full max-w-7xl mx-auto"
            >
              {activeTab === 'dashboard' && <Dashboard />}
              {activeTab === 'simulator' && <Simulator />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

function NavButton({ active, onClick, icon, text }: any) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-4 py-3 rounded-none transition-all border-2 border-black font-['Space_Grotesk'] font-bold tracking-wider text-sm uppercase ${
        active 
          ? 'bg-black text-white shadow-[4px_4px_0_0_rgba(255,255,255,1)] translate-x-[-2px] translate-y-[-2px]' 
          : 'bg-white text-black shadow-[4px_4px_0_0_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0_0_rgba(0,0,0,1)] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none'
      }`}
    >
      {icon}
      <span>{text}</span>
    </button>
  );
}
