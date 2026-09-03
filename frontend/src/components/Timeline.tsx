import { CheckCircle2, AlertTriangle, ShieldX, MessageSquare, Info } from "lucide-react";
import { motion } from "framer-motion";

export default function Timeline({ items = [] }: { items: any[] }) {
  return (
    <div className="relative border-l border-white/10 ml-4 space-y-8 pb-8 pt-4">
      {items.map((item, i) => {
        let Icon = Info;
        let color = "text-[#00f0ff] bg-[#00f0ff]/10 border-[#00f0ff]/30 shadow-[0_0_10px_rgba(0,240,255,0.2)]";
        
        if (item.severity === "warning") {
          Icon = AlertTriangle;
          color = "text-[#ffea00] bg-[#ffea00]/10 border-[#ffea00]/30 shadow-[0_0_10px_rgba(255,234,0,0.2)]";
        } else if (item.severity === "critical") {
          Icon = ShieldX;
          color = "text-[#ff003c] bg-[#ff003c]/10 border-[#ff003c]/30 shadow-[0_0_10px_rgba(255,0,60,0.2)]";
        } else if (item.event_type === "check") {
          Icon = CheckCircle2;
          color = "text-[#39ff14] bg-[#39ff14]/10 border-[#39ff14]/30 shadow-[0_0_10px_rgba(57,255,20,0.2)]";
        } else if (item.event_type === "reason") {
          Icon = MessageSquare;
          color = "text-[#b026ff] bg-[#b026ff]/10 border-[#b026ff]/30 shadow-[0_0_10px_rgba(176,38,255,0.2)]";
        }

        return (
          <motion.div 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20, delay: i * 0.1 }}
            key={`${item.step_number}-${item.timestamp}`} 
            className="relative pl-10"
          >
            <div className={`absolute -left-[16px] top-4 w-8 h-8 rounded-full border flex items-center justify-center ${color} z-10`}>
              <Icon size={14} />
            </div>
            <div className={`glass-panel p-5 hover:border-white/20 transition-all`}>
              <div className="flex justify-between items-start mb-3">
                <h4 className="font-light text-lg text-white/90 uppercase tracking-widest">{item.title}</h4>
                <span className="text-xs text-white/50 font-mono">
                  {new Date(item.timestamp + (item.timestamp.endsWith('Z') || item.timestamp.includes('+') ? '' : 'Z')).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm text-white/70 font-light leading-relaxed">{item.detail}</p>
              
              <span className="inline-block mt-4 px-2 py-1 bg-white/5 text-white/50 border border-white/10 font-mono text-[10px] uppercase tracking-widest rounded">
                Step {item.step_number}: {item.event_type}
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
