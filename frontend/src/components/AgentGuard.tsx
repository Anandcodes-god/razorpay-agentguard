import { useEffect, useState } from "react";
import { Activity, ArrowLeft, History, ShieldCheck, Terminal } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import Dashboard from "./Dashboard";
import Simulator from "./Simulator";

type Tab = "dashboard" | "simulator";
type AgentGuardProps = { onBack: () => void };

export default function AgentGuard({ onBack }: AgentGuardProps) {
  const [activeTab, setActiveTab] = useState<Tab>((window.location.hash.replace("#", "") as Tab) || "simulator");
  useEffect(() => { const handleHashChange = () => { const hash = window.location.hash.replace("#", "") as Tab; if (hash === "dashboard" || hash === "simulator") setActiveTab(hash); }; window.addEventListener("hashchange", handleHashChange); return () => window.removeEventListener("hashchange", handleHashChange); }, []);
  const changeTab = (tab: Tab) => { setActiveTab(tab); window.location.hash = tab; };
  return <div className="control-plane">
    <aside className="control-rail"><div className="rail-brand"><span className="rail-mark">AG</span><span>AGENT<br /><b>GUARD</b></span></div><div className="rail-label">CONTROL</div><nav className="rail-nav"><NavButton active={activeTab === "dashboard"} onClick={() => changeTab("dashboard")} icon={<Activity size={16} />} text="DASHBOARD" /><NavButton active={activeTab === "simulator"} onClick={() => changeTab("simulator")} icon={<History size={16} />} text="SIMULATOR" /></nav><div className="rail-bottom"><span className="rail-label">SYSTEM</span><div className="rail-live"><span className="status-dot" /> ONLINE</div><button className="rail-exit" onClick={onBack}><ArrowLeft size={14} /> BACK TO EXPERIENCE</button></div></aside>
    <div className="control-main"><header className="control-header"><div><span className="eyebrow">AGENTGUARD / CONTROL PLANE</span><h1>{activeTab === "dashboard" ? "Operational overview" : "Scenario simulator"}</h1></div><div className="control-meta"><span><Terminal size={14} /> ENV: SANDBOX</span><span><ShieldCheck size={14} /> POLICY ENGINE ONLINE</span></div></header><main className="control-content"><AnimatePresence mode="wait"><motion.div key={activeTab} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: .25 }} className="control-view">{activeTab === "dashboard" ? <Dashboard /> : <Simulator />}</motion.div></AnimatePresence></main></div>
  </div>;
}

function NavButton({ active, onClick, icon, text }: { active: boolean; onClick: () => void; icon: React.ReactNode; text: string }) {
  return <button onClick={onClick} className={`rail-button ${active ? "rail-button--active" : ""}`}>{icon}<span>{text}</span></button>;
}