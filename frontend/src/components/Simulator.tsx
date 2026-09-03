import { useState, useEffect } from "react";
import { Play, RotateCcw, AlertTriangle, CheckCircle, ArrowLeft, ScanSearch } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Timeline from "./Timeline";

const SCENARIOS = [
  { id: 1, name: "Normal Purchase", desc: "Agent buys groceries within budget." },
  { id: 2, name: "Unknown Agent", desc: "Unverified agent attempts purchase." },
  { id: 3, name: "Budget Exceeded", desc: "Purchase exceeds max allowed limit." },
  { id: 4, name: "Category Drift", desc: "Agent buys gaming items on grocery intent." },
  { id: 5, name: "Velocity Spike", desc: "Agent suddenly makes 12 purchases." }
];

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function Simulator() {
  const [phase, setPhase] = useState<'idle' | 'processing' | 'result'>('idle');
  const [result, setResult] = useState<any>(null);
  const [activeScenario, setActiveScenario] = useState<any>(null);

  const runScenario = async (scenario: any) => {
    setActiveScenario(scenario);
    setPhase('processing');
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/simulate/run?scenario_id=${scenario.id}`, { method: "POST" });
      const data = await res.json();
      setResult(data);
      // Fast transition to keep UI snappy
      setTimeout(() => setPhase('result'), 300);
    } catch (e) {
      console.error(e);
      setPhase('idle');
    }
  };

  const seedDB = async () => {
    await fetch(`${API_BASE}/api/seed`, { method: "POST" });
    alert("Database Seeded!");
  };

  return (
    <div className="min-h-full w-full flex flex-col items-center relative py-12">
      {/* Background ambient glow based on phase */}
      <motion.div 
        className="absolute inset-0 z-0 pointer-events-none opacity-20 transition-colors duration-1000"
        animate={{
          background: phase === 'idle' ? 'radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.2) 0%, transparent 70%)' :
                      phase === 'processing' ? 'radial-gradient(circle at 50% 50%, rgba(176, 38, 255, 0.4) 0%, transparent 50%)' :
                      result?.actual_decision === 'ALLOW' ? 'radial-gradient(circle at 50% 50%, rgba(57, 255, 20, 0.3) 0%, transparent 80%)' :
                      result?.actual_decision === 'REVIEW' ? 'radial-gradient(circle at 50% 50%, rgba(255, 234, 0, 0.3) 0%, transparent 80%)' :
                      'radial-gradient(circle at 50% 50%, rgba(255, 0, 60, 0.3) 0%, transparent 80%)'
        }}
      />

      <AnimatePresence mode="wait">
        
        {/* PHASE 1: IDLE / INTENT SELECTION */}
        {phase === 'idle' && (
          <motion.div 
            key="idle"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-5xl z-10 mt-16"
          >
            <div className="text-center mb-12">
              <h2 className="text-3xl font-light text-white/90 tracking-widest uppercase mb-4 shadow-[0_0_20px_rgba(0,240,255,0.3)]">Inject Scenario Intent</h2>
              <p className="text-white/50 font-mono text-sm">Select a transaction payload to pipe into the AgentGuard Risk Engine.</p>
              <button onClick={seedDB} className="mt-4 px-4 py-2 rounded-full border border-white/10 text-white/50 font-mono text-xs hover:bg-white/5 hover:text-white/90 transition-all">
                <RotateCcw size={12} className="inline mr-2" />
                RESET DATABASE STATE
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {SCENARIOS.map((s, i) => (
                <motion.div 
                  key={s.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  whileHover={{ scale: 1.05, borderColor: 'rgba(0, 240, 255, 0.5)', boxShadow: '0 0 20px rgba(0, 240, 255, 0.2)' }}
                  onClick={() => runScenario(s)}
                  className="glass-panel p-6 cursor-pointer border border-white/10 hover:bg-white/5 transition-all group flex flex-col items-center text-center"
                >
                  <div className="w-12 h-12 rounded-full border border-white/20 bg-white/5 flex items-center justify-center mb-4 group-hover:bg-[#00f0ff]/20 group-hover:text-[#00f0ff] transition-colors">
                    <Play size={16} />
                  </div>
                  <h4 className="font-light text-lg text-white/90 tracking-widest uppercase mb-2">{s.name}</h4>
                  <p className="text-xs text-white/50 font-mono">{s.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* PHASE 2: PROCESSING (The GenUI Constructing Phase) */}
        {phase === 'processing' && (
          <motion.div 
            key="processing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="flex flex-col items-center justify-center z-10 mt-32"
          >
            {/* The Habit-Loop Spinner Morph */}
            <motion.div 
              layoutId="morph-orb"
              animate={{ rotate: 360, scale: [1, 1.2, 1] }}
              transition={{ rotate: { duration: 2, repeat: Infinity, ease: "linear" }, scale: { duration: 1, repeat: Infinity } }}
              className="w-32 h-32 rounded-full border-t-2 border-l-2 border-[#b026ff] shadow-[0_0_50px_rgba(176,38,255,0.5)] flex items-center justify-center relative"
            >
              <div className="w-16 h-16 rounded-full bg-[#b026ff]/20 blur-md absolute animate-pulse"></div>
              <ScanSearch size={32} className="text-[#b026ff]" />
            </motion.div>
            
            <motion.h3 
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="mt-8 text-xl font-mono tracking-widest text-[#b026ff] uppercase"
            >
              Constructing Assessment Pipeline...
            </motion.h3>
            <p className="mt-2 font-mono text-xs text-white/40">Evaluating intent for '{activeScenario?.name}'</p>
          </motion.div>
        )}

        {/* PHASE 3: RESULT REVEAL (GenUI Explosion) */}
        {phase === 'result' && result && (
          <motion.div 
            key="result"
            initial={{ opacity: 0, height: 0, scale: 0.8 }}
            animate={{ opacity: 1, height: 'auto', scale: 1 }}
            className="w-full max-w-5xl z-10 flex flex-col relative"
          >
            <button onClick={() => setPhase('idle')} className="absolute -top-12 left-0 flex items-center gap-2 text-white/50 hover:text-white transition-colors font-mono text-xs uppercase tracking-widest">
              <ArrowLeft size={14} /> Back to Intents
            </button>
            
            <div className={`glass-panel overflow-hidden border ${
                result.actual_decision === 'ALLOW' ? 'border-[#39ff14]/50 shadow-[0_0_40px_rgba(57,255,20,0.15)]' :
                result.actual_decision === 'REVIEW' ? 'border-[#ffea00]/50 shadow-[0_0_40px_rgba(255,234,0,0.15)]' :
                'border-[#ff003c]/50 shadow-[0_0_40px_rgba(255,0,60,0.15)]'
              }`}
            >
              <div className={`p-8 border-b border-white/10 bg-gradient-to-br ${
                result.actual_decision === 'ALLOW' ? 'from-[#39ff14]/20 to-transparent' :
                result.actual_decision === 'REVIEW' ? 'from-[#ffea00]/20 to-transparent' :
                'from-[#ff003c]/20 to-transparent'
              }`}>
                <div className="flex items-center gap-6">
                  {/* The Reward Burst */}
                  <motion.div 
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: "spring", damping: 12 }}
                    className={`p-6 rounded-full bg-black/60 border backdrop-blur-md ${
                      result.actual_decision === 'ALLOW' ? 'text-[#39ff14] border-[#39ff14]/50 shadow-[0_0_30px_rgba(57,255,20,0.5)]' :
                      result.actual_decision === 'REVIEW' ? 'text-[#ffea00] border-[#ffea00]/50 shadow-[0_0_30px_rgba(255,234,0,0.5)]' :
                      'text-[#ff003c] border-[#ff003c]/50 shadow-[0_0_30px_rgba(255,0,60,0.5)]'
                    }`}
                  >
                    {result.actual_decision === 'ALLOW' && <CheckCircle size={48} />}
                    {result.actual_decision === 'REVIEW' && <AlertTriangle size={48} />}
                    {result.actual_decision === 'BLOCK' && <AlertTriangle size={48} />}
                  </motion.div>
                  
                  <div>
                    <h2 className={`text-5xl font-light tracking-widest uppercase mb-2 ${
                      result.actual_decision === 'ALLOW' ? 'neon-text-green' :
                      result.actual_decision === 'REVIEW' ? 'text-[#ffea00]' :
                      'text-[#ff003c]'
                    }`}>{result.actual_decision}</h2>
                    <div className="flex items-center gap-4">
                      <p className={`text-xs font-mono tracking-widest uppercase border px-3 py-1.5 rounded inline-block ${result.actual_decision === 'BLOCK' ? 'bg-[#ff003c]/10 border-[#ff003c]/30 text-[#ff003c]' : 'bg-white/5 border-white/10 text-white/70'}`}>
                        Expected: {result.scenario.expected_decision} <span className="mx-2 opacity-50">|</span> Match: {result.match ? 'YES' : 'NO'}
                      </p>
                      <p className="text-white/50 font-mono text-xs">Scenario: {activeScenario?.name}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* GenUI Constructed Timeline */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="p-8 bg-black/40"
              >
                <h4 className="font-mono text-xs text-white/50 uppercase tracking-widest mb-6">Generated Audit Trail</h4>
                <Timeline items={result.timeline} />
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
