import { useState, useEffect } from "react";
import { Shield, ShieldAlert, ShieldCheck, Activity } from "lucide-react";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/dashboard/stats")
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(e => console.error(e));
  }, []);

  if (!stats) return <div className="animate-pulse flex gap-4"><div className="h-32 w-full bg-white border-4 border-black"></div></div>;

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-10">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div variants={item}><StatCard title="Total Assessments" value={stats.total_assessments} icon={<Activity strokeWidth={2.5} />} bg="bg-[#00E5FF]" /></motion.div>
        <motion.div variants={item}><StatCard title="Allowed" value={stats.allowed} icon={<ShieldCheck strokeWidth={2.5} />} bg="bg-[#4ADE80]" /></motion.div>
        <motion.div variants={item}><StatCard title="Review Required" value={stats.reviewed} icon={<ShieldAlert strokeWidth={2.5} />} bg="bg-[#FFD600]" /></motion.div>
        <motion.div variants={item}><StatCard title="Blocked" value={stats.blocked} icon={<Shield strokeWidth={2.5} />} bg="bg-[#FF4500]" text="text-white" /></motion.div>
      </div>

      <motion.div variants={item} className="bg-white border-4 border-black shadow-[8px_8px_0_0_rgba(0,0,0,1)] p-8 relative">
        <h3 className="text-2xl font-black font-['Space_Grotesk'] mb-6 text-black uppercase tracking-tight flex items-center gap-3">
          <Activity size={28} strokeWidth={3} className="text-[#FF90E8]" />
          Recent Assessments
        </h3>
        <div className="overflow-x-auto border-t-4 border-black">
          <table className="w-full text-left border-collapse mt-4">
            <thead>
              <tr className="text-black font-bold font-['Space_Grotesk'] uppercase tracking-widest text-sm">
                <th className="py-4 px-2 border-b-4 border-black">ID</th>
                <th className="py-4 px-2 border-b-4 border-black">Decision</th>
                <th className="py-4 px-2 border-b-4 border-black text-right">Time</th>
              </tr>
            </thead>
            <tbody>
              {stats.recent_assessments?.map((a: any, i: number) => (
                <motion.tr 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 + 0.3 }}
                  key={a.id} 
                  className="hover:bg-[#F4F4F0] transition-colors font-medium border-b-2 border-black/20 group"
                >
                  <td className="py-4 px-2 text-sm font-['Space_Grotesk'] font-bold text-black group-hover:translate-x-2 transition-transform">{a.id.split('-')[0]}</td>
                  <td className="py-4 px-2">
                    <span className={`px-3 py-1.5 text-xs font-black font-['Space_Grotesk'] tracking-widest uppercase border-2 border-black shadow-[2px_2px_0_0_rgba(0,0,0,1)] inline-block ${
                      a.policy_decision === 'ALLOW' ? 'bg-[#4ADE80] text-black' :
                      a.policy_decision === 'REVIEW' ? 'bg-[#FFD600] text-black' :
                      'bg-[#FF4500] text-white'
                    }`}>
                      {a.policy_decision}
                    </span>
                  </td>
                  <td className="py-4 px-2 text-sm text-black font-bold text-right group-hover:-translate-x-2 transition-transform">{new Date(a.created_at + (a.created_at.endsWith('Z') ? '' : 'Z')).toLocaleString()}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}

function StatCard({ title, value, icon, bg, text = "text-black" }: any) {
  return (
    <div className={`p-6 bg-white border-4 border-black shadow-[6px_6px_0_0_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0_0_rgba(0,0,0,1)] transition-all cursor-default`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-black font-bold font-['Space_Grotesk'] text-xs tracking-widest uppercase mb-2">{title}</p>
          <p className="text-5xl font-black text-black tracking-tighter">{value}</p>
        </div>
        <div className={`p-3 border-4 border-black ${bg} ${text} shadow-[4px_4px_0_0_rgba(0,0,0,1)] transform -rotate-3`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
