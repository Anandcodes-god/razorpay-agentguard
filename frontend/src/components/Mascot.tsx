import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';

export default function Mascot() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const controls = useAnimation();

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Calculate position relative to center for parallax
      const x = (e.clientX / window.innerWidth - 0.5) * 100;
      const y = (e.clientY / window.innerHeight - 0.5) * 100;
      setMousePos({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="fixed bottom-12 right-12 z-50 pointer-events-none flex flex-col items-center justify-center hidden md:flex">
      {/* Sentient Orb */}
      <motion.div 
        animate={{ 
          x: mousePos.x * 0.2, 
          y: mousePos.y * 0.2 
        }}
        transition={{ type: "spring", damping: 30, stiffness: 200 }}
        className="w-16 h-16 rounded-full flex items-center justify-center relative"
        style={{
          background: 'radial-gradient(circle at 30% 30%, rgba(0, 240, 255, 1) 0%, rgba(0, 100, 255, 0.8) 50%, rgba(0, 0, 50, 0.9) 100%)',
          boxShadow: '0 0 30px rgba(0, 240, 255, 0.5), inset 0 0 10px rgba(255, 255, 255, 0.5)'
        }}
      >
        {/* Core pulsing energy */}
        <motion.div 
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="absolute inset-2 rounded-full bg-white blur-md"
        />
        
        {/* The "Eye" tracker */}
        <motion.div 
            animate={{ 
              x: mousePos.x * 0.4, 
              y: mousePos.y * 0.4 
            }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="w-4 h-4 bg-white rounded-full absolute shadow-[0_0_10px_white]"
        />
      </motion.div>
      
      {/* Dynamic Status Text */}
      <motion.div 
        animate={{ opacity: 0.5 }}
        whileHover={{ opacity: 1 }}
        className="mt-4 font-mono text-[10px] text-[#00f0ff] uppercase tracking-widest text-center shadow-lg"
      >
        Agent Core <br/>Active
      </motion.div>
    </div>
  );
}
