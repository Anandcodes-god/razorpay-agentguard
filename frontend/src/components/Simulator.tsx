import { useState } from "react";
import { Play, RotateCcw, AlertTriangle, CheckCircle, Info, ScanSearch } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Timeline from "./Timeline";

const SCENARIOS = [
  { id: 1, name: "Normal Purchase", desc: "Agent buys groceries within budget." },
  { id: 2, name: "Unknown Agent", desc: "Unverified agent attempts purchase." },
  { id: 3, name: "Budget Exceeded", desc: "Purchase exceeds max allowed limit." },
  { id: 4, name: "Category Drift", desc: "Agent buys gaming items on grocery intent." },
  { id: 5, name: "Velocity Spike", desc: "Agent suddenly makes 12 purchases." }
];

export default function Simulator() {
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeScenario, setActiveScenario] = useState<number | null>(null);

  const runScenario = async (id: number) => {
    setActiveScenario(id);
    setRunning(true);
    setResult(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/simulate/run?scenario_id=${id}`, { method: "POST" });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  const seedDB = async () => {
    await fetch(`http://127.0.0.1:8000/api/seed`, { method: "POST" });
    alert("Database Seeded!");
  };

  return (
    <div className="flex gap-8 h-full">
      {/* Left panel: Scenarios */}
      <motion.div 
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-1/3 bg-white p-6 border-4 border-black shadow-[8px_8px_0_0_rgba(0,0,0,1)] overflow-y-auto scrollbar-hide flex flex-col"
      >
        <div className="flex justify-between items-center mb-6 sticky top-0 bg-white pb-2 z-10 border-b-4 border-black">
          <h3 className="font-black font-['Space_Grotesk'] text-2xl text-black uppercase tracking-tight">Scenarios</h3>
          <button onClick={seedDB} className="p-2 border-2 border-black bg-[#FF90E8] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none shadow-[2px_2px_0_0_rgba(0,0,0,1)] transition-all tooltip" title="Reset DB">
            <RotateCcw size={20} strokeWidth={2.5} />
          </button>
        </div>
        
        <div className="space-y-4 flex-1">
          {SCENARIOS.map((s, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              key={s.id} 
              className={`p-4 border-4 border-black transition-all ${activeScenario === s.id ? 'bg-[#00E5FF] shadow-[4px_4px_0_0_rgba(0,0,0,1)] translate-x-[-2px] translate-y-[-2px]' : 'bg-[#F4F4F0] hover:bg-[#FFD600] hover:shadow-[4px_4px_0_0_rgba(0,0,0,1)] hover:translate-x-[-2px] hover:translate-y-[-2px]'}`}
            >
              <h4 className="font-black font-['Space_Grotesk'] text-lg text-black tracking-tight">{s.name}</h4>
              <p className="text-sm text-black font-medium mt-1 mb-4">{s.desc}</p>
              <button
                disabled={running}
                onClick={() => runScenario(s.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-black text-white text-sm font-bold font-['Space_Grotesk'] tracking-widest uppercase border-2 border-black shadow-[4px_4px_0_0_rgba(255,255,255,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none active:bg-[#FF4500] active:text-white transition-all disabled:opacity-50"
              >
                {running && activeScenario === s.id ? (
                  <RotateCcw className="animate-spin" size={18} strokeWidth={3} />
                ) : (
                  <Play size={18} strokeWidth={3} />
                )}
                {running && activeScenario === s.id ? "Running" : "Execute"}
              </button>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Right panel: Timeline & Results */}
      <motion.div 
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-2/3 bg-white border-4 border-black shadow-[8px_8px_0_0_rgba(0,0,0,1)] flex flex-col overflow-hidden relative"
      >
        <AnimatePresence mode="wait">
          {result ? (
            <motion.div 
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 overflow-y-auto scrollbar-hide flex flex-col"
            >
              <div className={`p-8 border-b-4 border-black ${
                result.actual_decision === 'ALLOW' ? 'bg-[#4ADE80]' :
                result.actual_decision === 'REVIEW' ? 'bg-[#FFD600]' :
                'bg-[#FF4500]'
              }`}>
                <div className="flex items-center gap-6">
                  <div className={`p-4 border-4 border-black bg-white shadow-[4px_4px_0_0_rgba(0,0,0,1)] ${
                    result.actual_decision === 'ALLOW' ? 'text-black' :
                    result.actual_decision === 'REVIEW' ? 'text-black' :
                    'text-[#FF4500]'
                  }`}>
                    {result.actual_decision === 'ALLOW' && <CheckCircle size={40} strokeWidth={2.5} />}
                    {result.actual_decision === 'REVIEW' && <AlertTriangle size={40} strokeWidth={2.5} />}
                    {result.actual_decision === 'BLOCK' && <AlertTriangle size={40} strokeWidth={2.5} />}
                  </div>
                  <div>
                    <h2 className={`text-5xl font-black font-['Space_Grotesk'] tracking-tighter mb-2 ${
                      result.actual_decision === 'ALLOW' ? 'text-black' :
                      result.actual_decision === 'REVIEW' ? 'text-black' :
                      'text-white'
                    }`}>{result.actual_decision}</h2>
                    <p className={`text-sm font-bold font-['Space_Grotesk'] tracking-wider uppercase border-2 border-black inline-block px-2 py-1 ${result.actual_decision === 'BLOCK' ? 'bg-white text-black' : 'bg-white text-black'}`}>
                      Expected: {result.scenario.expected_decision} <span className="mx-2">|</span> Match: {result.match ? '✅' : '❌'}
                    </p>
                  </div>
                </div>
              </div>
              <div className="p-8 flex-1 bg-[#F4F4F0]">
                <Timeline items={result.timeline} />
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex flex-col items-center justify-center p-12 text-center bg-[#F4F4F0]"
            >
              <div className="w-24 h-24 mb-6 border-4 border-black border-dashed flex items-center justify-center bg-white shadow-[4px_4px_0_0_rgba(0,0,0,1)] animate-bounce">
                <ScanSearch size={40} strokeWidth={2.5} className="text-black" />
              </div>
              <h3 className="text-3xl font-black font-['Space_Grotesk'] text-black mb-4 uppercase tracking-tight">Awaiting Signal</h3>
              <p className="max-w-sm text-base text-black font-medium">Select a scenario from the left panel to execute a transaction through the Risk Engine.</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
