import { CheckCircle2, AlertTriangle, ShieldX, MessageSquare, Info } from "lucide-react";
import { motion } from "framer-motion";

export default function Timeline({ items = [] }: { items: any[] }) {
  return (
    <div className="relative border-l-4 border-black ml-4 space-y-10 pb-8 pt-4">
      {items.map((item, i) => {
        let Icon = Info;
        let color = "bg-[#00E5FF] text-black";
        
        if (item.severity === "warning") {
          Icon = AlertTriangle;
          color = "bg-[#FFD600] text-black";
        } else if (item.severity === "critical") {
          Icon = ShieldX;
          color = "bg-[#FF4500] text-white";
        } else if (item.event_type === "check") {
          Icon = CheckCircle2;
          color = "bg-[#4ADE80] text-black";
        } else if (item.event_type === "reason") {
          Icon = MessageSquare;
          color = "bg-[#FF90E8] text-black";
        }

        return (
          <motion.div 
            initial={{ opacity: 0, x: -20, rotate: -2 }}
            animate={{ opacity: 1, x: 0, rotate: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20, delay: i * 0.1 }}
            key={i} 
            className="relative pl-10"
          >
            <div className={`absolute -left-[23px] top-1 w-10 h-10 border-4 border-black flex items-center justify-center ${color} z-10 shadow-[2px_2px_0_0_rgba(0,0,0,1)]`}>
              <Icon size={20} strokeWidth={2.5} />
            </div>
            <div className={`bg-white border-4 border-black p-5 shadow-[6px_6px_0_0_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[4px_4px_0_0_rgba(0,0,0,1)] transition-all`}>
              <div className="flex justify-between items-start mb-3">
                <h4 className="font-black font-['Space_Grotesk'] text-lg text-black uppercase tracking-tight">{item.title}</h4>
                <span className="text-xs text-black font-bold font-['Space_Grotesk'] border-2 border-black px-2 py-1 bg-[#F4F4F0] shadow-[2px_2px_0_0_rgba(0,0,0,1)]">
                  {new Date(item.timestamp + (item.timestamp.endsWith('Z') || item.timestamp.includes('+') ? '' : 'Z')).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm text-black font-medium leading-relaxed">{item.detail}</p>
              
              <span className="inline-block mt-4 px-3 py-1 bg-black text-white font-['Space_Grotesk'] font-bold text-[10px] uppercase tracking-widest">
                Step {item.step_number}: {item.event_type}
              </span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
