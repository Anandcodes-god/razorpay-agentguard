import { useState } from "react";
import { AlertTriangle, ArrowLeft, ArrowRight, CheckCircle, Play, RotateCcw, ScanSearch, ShieldX } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import Timeline from "./Timeline";

const SCENARIOS = [
  { id: 1, name: "Normal Purchase", desc: "Agent buys groceries within budget." },
  { id: 2, name: "Unknown Agent", desc: "Unverified agent attempts purchase." },
  { id: 3, name: "Budget Exceeded", desc: "Purchase exceeds max allowed limit." },
  { id: 4, name: "Category Drift", desc: "Agent buys gaming items on grocery intent." },
  { id: 5, name: "Velocity Spike", desc: "Agent suddenly makes 12 purchases." },
];

const API_BASE = import.meta.env.VITE_API_URL || "";
const API_HEADERS = import.meta.env.VITE_ADMIN_API_KEY
  ? { "X-API-Key": import.meta.env.VITE_ADMIN_API_KEY }
  : undefined;
const USE_DEV_PROXY = import.meta.env.DEV && !import.meta.env.VITE_API_URL;

type Phase = "idle" | "processing" | "result";
const PIPELINE_STAGES = ["REQUEST", "IDENTITY", "CONTRACT", "POLICY", "DECISION", "AUDIT"];

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
    if (!API_HEADERS && !USE_DEV_PROXY) {
      setError("Simulator access is not configured. Set VITE_ADMIN_API_KEY in frontend/.env and restart Vite.");
      setPhase("idle");
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/simulate/run?scenario_id=${scenario.id}`, {
        method: "POST",
        headers: API_HEADERS,
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
    if (!API_HEADERS && !USE_DEV_PROXY) {
      setError("Database reset is not configured. Set VITE_ADMIN_API_KEY in frontend/.env and restart Vite.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/seed`, { method: "POST", headers: API_HEADERS });
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
        className="simulator-atmosphere"
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
          <motion.div key="idle" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }} className="simulator-view">
            <div className="simulator-heading">
              <div><span className="eyebrow">DEMO / FIVE DOCUMENTED SCENARIOS</span><h2>Inject scenario intent</h2><p>Select a transaction payload to pipe into the AgentGuard Risk Engine.</p></div>
              <button onClick={seedDB} className="reset-button">
                <RotateCcw size={12} className="inline mr-2" />RESET DATABASE STATE
              </button>
              {seedMsg && <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="ml-4 text-[#39ff14] font-mono text-xs">{seedMsg}</motion.span>}
              {error && <div className="mt-4 text-[#ff003c] font-mono text-sm">{error}</div>}
            </div>
            <div className="scenario-grid">
              {SCENARIOS.map((scenario, index) => (
                <motion.button type="button" key={scenario.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} onClick={() => runScenario(scenario)} className="scenario-card">
                  <span className="scenario-number">0{scenario.id}</span><span className="scenario-icon"><Play size={14} /></span><h4>{scenario.name}</h4><p>{scenario.desc}</p><span className="scenario-action">RUN SCENARIO <ArrowRight size={13} /></span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {phase === "processing" && (
          <motion.div key="processing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pipeline-view">
            <div className="pipeline-icon"><ScanSearch size={26} /></div><span className="eyebrow">ASSESSMENT PIPELINE / ACTIVE</span><h3>Evaluating {activeScenario?.name}</h3><div className="pipeline-stages">{PIPELINE_STAGES.map((stage, index) => <div className="pipeline-stage" key={stage}><span>{index + 1}</span><strong>{stage}</strong></div>)}</div>
          </motion.div>
        )}

        {phase === "result" && result && (
          <motion.div key="result" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="simulator-result">
            <button onClick={() => setPhase("idle")} className="back-button"><ArrowLeft size={14} /> BACK TO SCENARIOS</button>
            <div className="result-panel glass-panel">
              <div className="result-summary">
                <div className="result-icon">
                    {decision === "ALLOW" && <CheckCircle size={48} className="text-[#39ff14]" />}
                    {decision === "REVIEW" && <AlertTriangle size={48} className="text-[#ffea00]" />}
                    {decision === "BLOCK" && <ShieldX size={48} className="text-[#ff003c]" />}
                  </div>
                  <div className="result-heading">
                    <span className="eyebrow">SCENARIO {String(result.scenario.id).padStart(2, "0")} / DECISION</span><h2>{decision}</h2>
                    <p>Expected: {result.scenario.expected_decision} <span /> Match: {result.match ? "YES" : "NO"}</p>
                  </div>
                </div>
              <div className="result-timeline">
                <h4>GENERATED AUDIT TRAIL</h4>
                <Timeline items={result.timeline} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
