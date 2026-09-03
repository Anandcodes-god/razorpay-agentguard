import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield } from 'lucide-react';

export default function Landing({ onComplete }: { onComplete: () => void }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    const updateMousePosition = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', updateMousePosition);
    return () => window.removeEventListener('mousemove', updateMousePosition);
  }, []);

  const handleClick = () => {
    setIsFading(true);
    setTimeout(onComplete, 500);
  };

  return (
    <motion.div 
      className="fixed inset-0 bg-[#030305] z-50 overflow-hidden flex flex-col items-center justify-center"
      initial={{ opacity: 1 }}
      animate={{ opacity: isFading ? 0 : 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Glowing Cursor Spotlight */}
      <div 
        className="pointer-events-none absolute inset-0 z-0 transition-opacity duration-300"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0, 240, 255, 0.08), transparent 40%)`
        }}
      />
      
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 z-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      {/* Content */}
      <div className="z-10 flex flex-col items-center text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mb-8 p-5 rounded-2xl bg-[#00f0ff]/5 border border-[#00f0ff]/20 shadow-[0_0_30px_rgba(0,240,255,0.1)] relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-[#00f0ff]/20 to-transparent opacity-50"></div>
          <Shield size={64} className="text-[#00f0ff] relative z-10" />
        </motion.div>
        
        <motion.h1 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl md:text-7xl font-light tracking-widest text-white mb-6 uppercase drop-shadow-2xl"
        >
          Agent<span className="text-[#00f0ff] font-bold">Guard</span>
        </motion.h1>
        
        <motion.p 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-white/50 font-mono tracking-widest text-sm md:text-base max-w-xl mb-12 uppercase"
        >
          Securing Autonomous AI Transactions on Razorpay
        </motion.p>
        
        <motion.button 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          onClick={handleClick}
          className="relative overflow-hidden group px-8 py-4 bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff] font-mono text-sm tracking-widest uppercase hover:bg-[#00f0ff]/20 hover:scale-105 hover:shadow-[0_0_30px_rgba(0,240,255,0.3)] transition-all duration-300 rounded"
        >
          <span className="relative z-10">Initialize Sandbox</span>
          <div className="absolute inset-0 h-full w-0 bg-gradient-to-r from-transparent via-[#00f0ff]/20 to-transparent group-hover:w-full transition-all duration-500 ease-out"></div>
        </motion.button>
      </div>
    </motion.div>
  );
}
