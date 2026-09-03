import { useState } from "react";
import { AlertTriangle, ArrowLeft, CheckCircle, Play, RotateCcw, ScanSearch, ShieldX } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import Timeline from "./Timeline";

const SCENARIOS = [
  { id: 1, name: "Normal Purchase", desc: "Agent buys groceries within budget." },
  { id: 2, name: "Unknown Agent", desc: "Unverified agent attempts purchase." },
  { id: 3, name: "Budget Exceeded", desc: "Purchase exceeds max allowed limit." },
  { id: 4, name: "Category Drift", desc: "Agent buys gaming items on grocery intent." },
  { id: 5, name: "Velocity Spike", desc: "Agent suddenly makes 12 purchases." },
];

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type Phase = "idle" | "processing" | "result";

export default function Simulator() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [result, setResult] = useState<any>(null);
  const [activeScenario, setActiveScenario] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [seedMsg, setSeedMsg] = useState("");

  const runScenario = async (scenario: any) => {
    setActiveScenario(scenario);
    setPhase("processing");
    setResult(null);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/simulate/run?scenario_id=${scenario.id}`, {
        method: "POST",
      });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      setResult(await response.json());
      setTimeout(() => setPhase("result"), 300);
    } catch (requestError) {
      console.error(requestError);
      setError("Backend not reachable. Is the server running?");
      setPhase("idle");
    }
  };

  const seedDB = async () => {
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/seed`, { method: "POST" });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      setSeedMsg("State Reset");
      setTimeout(() => setSeedMsg(""), 2000);
    } catch (requestError) {
      console.error(requestError);
      setError("Database reset is unavailable. Check that DEBUG=true in the backend .env file.");
    }
  };

  const decision = result?.actual_decision;

  return (
    <div className="min-h-full w-full flex flex-col items-center relative py-12">
      <motion.div
        className="absolute inset-0 z-0 pointer-events-none opacity-20"
        animate={{
          background: phase === "processing"
            ? "radial-gradient(circle at 50% 50%, rgba(176, 38, 255, 0.4) 0%, transparent 50%)"
            : decision === "ALLOW"
              ? "radial-gradient(circle at 50% 50%, rgba(57, 255, 20, 0.3) 0%, transparent 80%)"
              : decision === "REVIEW"
                ? "radial-gradient(circle at 50% 50%, rgba(255, 234, 0, 0.3) 0%, transparent 80%)"
                : "radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.2) 0%, transparent 70%)",
        }}
      />

      <AnimatePresence mode="wait">
        {phase === "idle" && (
          <motion.div key="idle" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.1 }} className="w-full max-w-5xl z-10 mt-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-light text-white/90 tracking-widest uppercase mb-4">Inject Scenario Intent</h2>
              <p className="text-white/50 font-mono text-sm">Select a transaction payload to pipe into the AgentGuard Risk Engine.</p>
              <button onClick={seedDB} className="mt-4 px-4 py-2 rounded-full border border-white/10 text-white/50 font-mono text-xs hover:bg-white/5 hover:text-white/90 transition-all">
                <RotateCcw size={12} className="inline mr-2" />RESET DATABASE STATE
              </button>
              {seedMsg && <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="ml-4 text-[#39ff14] font-mono text-xs">{seedMsg}</motion.span>}
              {error && <div className="mt-4 text-[#ff003c] font-mono text-sm">{error}</div>}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {SCENARIOS.map((scenario, index) => (
                <motion.div key={scenario.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} whileHover={{ scale: 1.05 }} onClick={() => runScenario(scenario)} className="glass-panel p-6 cursor-pointer border border-white/10 hover:bg-white/5 transition-all group flex flex-col items-center text-center">
                  <div className="w-12 h-12 rounded-full border border-white/20 bg-white/5 flex items-center justify-center mb-4 group-hover:bg-[#00f0ff]/20 group-hover:text-[#00f0ff] transition-colors"><Play size={16} /></div>
                  <h4 className="font-light text-lg text-white/90 tracking-widest uppercase mb-2">{scenario.name}</h4>
                  <p className="text-xs text-white/50 font-mono">{scenario.desc}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {phase === "processing" && (
          <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center justify-center z-10 mt-32">
            <motion.div animate={{ rotate: 360, scale: [1, 1.2, 1] }} transition={{ rotate: { duration: 2, repeat: Infinity, ease: "linear" }, scale: { duration: 1, repeat: Infinity } }} className="w-32 h-32 rounded-full border-t-2 border-l-2 border-[#b026ff] shadow-[0_0_50px_rgba(176,38,255,0.5)] flex items-center justify-center"><ScanSearch size={32} className="text-[#b026ff]" /></motion.div>
            <h3 className="mt-8 text-xl font-mono tracking-widest text-[#b026ff] uppercase">Constructing Assessment Pipeline...</h3>
            <p className="mt-2 font-mono text-xs text-white/40">Evaluating intent for '{activeScenario?.name}'</p>
          </motion.div>
        )}

        {phase === "result" && result && (
          <motion.div key="result" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-5xl z-10 flex flex-col relative">
            <button onClick={() => setPhase("idle")} className="absolute -top-12 left-0 flex items-center gap-2 text-white/50 hover:text-white transition-colors font-mono text-xs uppercase tracking-widest"><ArrowLeft size={14} />Back to Intents</button>
            <div className="glass-panel overflow-hidden border border-white/20">
              <div className="p-8 border-b border-white/10">
                <div className="flex items-center gap-6">
                  <div className="p-6 rounded-full bg-black/60 border border-white/20">
                    {decision === "ALLOW" && <CheckCircle size={48} className="text-[#39ff14]" />}
                    {decision === "REVIEW" && <AlertTriangle size={48} className="text-[#ffea00]" />}
                    {decision === "BLOCK" && <ShieldX size={48} className="text-[#ff003c]" />}
                  </div>
                  <div>
                    <h2 className="text-5xl font-light tracking-widest uppercase mb-2">{decision}</h2>
                    <p className="text-xs font-mono tracking-widest uppercase border px-3 py-1.5 rounded inline-block">Expected: {result.scenario.expected_decision} | Match: {result.match ? "YES" : "NO"}</p>
                  </div>
                </div>
              </div>
              <div className="p-8 bg-black/40">
                <h4 className="font-mono text-xs text-white/50 uppercase tracking-widest mb-6">Generated Audit Trail</h4>
                <Timeline items={result.timeline} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
