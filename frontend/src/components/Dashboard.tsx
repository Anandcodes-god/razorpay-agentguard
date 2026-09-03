import { useState, useEffect } from "react";
import { Shield, ShieldAlert, ShieldCheck, Activity } from "lucide-react";
import { motion, type Variants } from "framer-motion";

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const API_HEADERS = { 'X-API-Key': import.meta.env.VITE_ADMIN_API_KEY || 'dev-secret' };

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/dashboard/stats`, { headers: API_HEADERS })
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

  if (error) return <div className="p-4 glass-panel border-[#ff003c] text-[#ff003c] font-mono">{error}</div>;
  if (!stats) return <div className="animate-pulse flex gap-4"><div className="h-32 w-full glass-panel"></div></div>;

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
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8 mt-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div variants={item}><StatCard title="Total Assessments" value={stats.total_assessments} icon={<Activity />} color="text-[#00f0ff]" /></motion.div>
        <motion.div variants={item}><StatCard title="Allowed" value={stats.allowed} icon={<ShieldCheck />} color="text-[#39ff14]" /></motion.div>
        <motion.div variants={item}><StatCard title="Review Required" value={stats.reviewed} icon={<ShieldAlert />} color="text-[#ffea00]" /></motion.div>
        <motion.div variants={item}><StatCard title="Blocked" value={stats.blocked} icon={<Shield />} color="text-[#ff003c]" /></motion.div>
      </div>

      <motion.div variants={item} className="glass-panel p-8 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#00f0ff]/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <h3 className="text-xl font-light mb-6 text-white/90 uppercase tracking-widest flex items-center gap-3">
          <Activity size={20} className="text-[#00f0ff]" />
          Recent Assessments
        </h3>
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
                  className="hover:bg-white/5 transition-colors font-light border-b border-white/5 group-row"
                >
                  <td className="py-4 px-2 text-sm font-mono text-white/70">{a.id.split('-')[0]}</td>
                  <td className="py-4 px-2">
                    <span className={`px-3 py-1 text-[10px] font-mono tracking-widest uppercase rounded-full border ${
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
    <div className={`p-6 glass-panel relative overflow-hidden group hover:border-white/20 transition-all`}>
      <div className={`absolute top-0 right-0 w-24 h-24 ${color} opacity-5 blur-2xl group-hover:opacity-20 transition-opacity`}>
         <div className="w-full h-full bg-current rounded-full"></div>
      </div>
      <div className="flex items-start justify-between relative z-10">
        <div>
          <p className="text-white/50 font-mono text-[10px] tracking-widest uppercase mb-2">{title}</p>
          <p className={`text-4xl font-light tracking-tight ${color}`}>{value}</p>
        </div>
        <div className={`p-2 rounded-lg bg-white/5 border border-white/10 ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
