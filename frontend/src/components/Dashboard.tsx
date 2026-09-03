import { useState, useEffect } from "react";
import { Shield, ShieldAlert, ShieldCheck, Activity } from "lucide-react";
import { motion, type Variants } from "framer-motion";

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/dashboard/stats`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch dashboard stats");
        return res.json();
      })
      .then(data => {
        setStats(data);
        setError(null);
      })
      .catch(e => {
        console.error(e);
        setError("Could not load dashboard data. Please ensure the backend is running.");
      });
  }, []);

  if (error) return <div className="dashboard-state dashboard-state--error"><ShieldAlert size={18} />{error}</div>;
  if (!stats) return <div className="dashboard-loading"><div /><div /><div /><div /></div>;

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="dashboard-view">
      <div className="dashboard-metrics">
        <motion.div variants={item}><StatCard title="Total Assessments" value={stats.total_assessments} icon={<Activity />} color="text-[#00f0ff]" /></motion.div>
        <motion.div variants={item}><StatCard title="Allowed" value={stats.allowed} icon={<ShieldCheck />} color="text-[#39ff14]" /></motion.div>
        <motion.div variants={item}><StatCard title="Review Required" value={stats.reviewed} icon={<ShieldAlert />} color="text-[#ffea00]" /></motion.div>
        <motion.div variants={item}><StatCard title="Blocked" value={stats.blocked} icon={<Shield />} color="text-[#ff003c]" /></motion.div>
      </div>

      <motion.div variants={item} className="dashboard-table-panel glass-panel">
        <div className="dashboard-panel-heading">
          <div>
            <span className="eyebrow">DECISION LINEAGE / LAST 24 HOURS</span>
            <h3><Activity size={18} /> Recent Assessments</h3>
          </div>
          <span className="dashboard-live"><span className="status-dot" /> LIVE</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse mt-2">
            <thead>
              <tr className="text-white/40 font-mono uppercase tracking-widest text-xs border-b border-white/10">
                <th className="py-4 px-2 font-normal">ID</th>
                <th className="py-4 px-2 font-normal">Decision</th>
                <th className="py-4 px-2 font-normal text-right">Score</th>
                <th className="py-4 px-2 font-normal text-right">Time</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_assessments?.map((a: any, i: number) => (
                <motion.tr 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 + 0.3 }}
                  key={a.id} 
                  className="dashboard-table-row"
                >
                  <td className="py-4 px-2 text-sm font-mono text-white/70">{a.id.split('-')[0]}</td>
                  <td className="py-4 px-2">
                    <span className={`decision-tag ${
                      a.policy_decision === 'ALLOW' ? 'bg-[#39ff14]/10 text-[#39ff14] border-[#39ff14]/30 shadow-[0_0_10px_rgba(57,255,20,0.2)]' :
                      a.policy_decision === 'REVIEW' ? 'bg-[#ffea00]/10 text-[#ffea00] border-[#ffea00]/30 shadow-[0_0_10px_rgba(255,234,0,0.2)]' :
                      'bg-[#ff003c]/10 text-[#ff003c] border-[#ff003c]/30 shadow-[0_0_10px_rgba(255,0,60,0.2)]'
                    }`}>
                      {a.policy_decision}
                    </span>
                  </td>
                  <td className="py-4 px-2 text-sm text-white/50 font-mono text-right">{a.overall_risk_score ?? 'N/A'}</td>
                  <td className="py-4 px-2 text-sm text-white/50 font-mono text-right">{new Date(a.created_at + (a.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className={`stat-card glass-panel ${color}`}>
      <div className="stat-card__heading">
        <div>
          <p className="text-white/50 font-mono text-[10px] tracking-widest uppercase mb-2">{title}</p>
          <p className="stat-card__value">{value}</p>
        </div>
        <div className="stat-card__icon">
          {icon}
        </div>
      </div>
    </div>
  );
}
