import { useEffect, useState } from "react";
import { ArrowDown, ArrowRight, Menu, ShieldCheck, X } from "lucide-react";
import SecurityCore from "./SecurityCore";

type LandingProps = { onComplete: () => void };
const stages = ["IDENTITY", "INTENT CONTRACT", "POLICY GATE", "TOOL CONTROL", "RISK REVIEW", "AUDIT"];
const incident = [["09:41:02", "agent.start()", "quiet"], ["09:41:03", "user.authenticate()", "quiet"], ["09:41:04", "tool.search()", "quiet"], ["09:41:05", "tool.payment()", "quiet"], ["09:41:05", "POLICY CHECK", "amber"], ["09:41:05", "CATEGORY DRIFT DETECTED", "red"], ["09:41:05", "GUARD.BLOCK()", "red"], ["09:41:06", "AUDIT.LOG()", "green"]];

export default function Landing({ onComplete }: LandingProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isEntering, setIsEntering] = useState(false);
  const [incidentStep, setIncidentStep] = useState(5);
  useEffect(() => { const timer = window.setInterval(() => setIncidentStep((step) => step >= incident.length - 1 ? 5 : step + 1), 700); return () => window.clearInterval(timer); }, []);
  const enterControl = () => {
    const audioContext = new AudioContext();
    [220, 330, 440].forEach((frequency, index) => {
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.frequency.value = frequency;
      oscillator.type = "sine";
      gain.gain.setValueAtTime(0.0001, audioContext.currentTime + index * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.04, audioContext.currentTime + index * 0.08 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + index * 0.08 + 0.16);
      oscillator.connect(gain).connect(audioContext.destination);
      oscillator.start(audioContext.currentTime + index * 0.08);
      oscillator.stop(audioContext.currentTime + index * 0.08 + 0.18);
    });
    setIsEntering(true);
    window.setTimeout(() => { void audioContext.close(); onComplete(); }, 650);
  };

  return <div className={`experience ${isEntering ? "experience--entering" : ""}`}>
    <header className="experience-nav"><a className="wordmark" href="#top" aria-label="AgentGuard home">AGENT<span>GUARD</span><sup>®</sup></a><div className="nav-status"><span className="status-dot" /> SYSTEM ONLINE</div><button className="icon-button menu-trigger" onClick={() => setMenuOpen(true)} aria-label="Open menu"><Menu size={18} /><span>MENU</span></button></header>
    {menuOpen && <div className="experience-menu" role="dialog" aria-modal="true" aria-label="Experience navigation"><button className="icon-button menu-close" onClick={() => setMenuOpen(false)} aria-label="Close menu"><X size={22} /></button><span className="eyebrow">NAV / CONTROL PLANE</span><nav>{["SYSTEM", "THREATS", "POLICIES", "ARCHITECTURE", "DEMO", "CONTROL PLANE"].map((item, index) => <a key={item} href={`#${item.toLowerCase().replace(" ", "-")}`} onClick={() => setMenuOpen(false)}><small>0{index + 1}</small>{item}<ArrowRight size={22} /></a>)}</nav></div>}

    <main id="top">
      <section className="hero-section section-frame"><div className="hero-copy"><span className="eyebrow">SECURITY CONTROL PLANE / RAZORPAY</span><h1><span className="hero-line">YOUR</span><span className="hero-line hero-word hero-word--wide">AGENTS</span><span className="hero-line">ARE</span><span className="hero-line hero-word--accent">NOT ALONE<span className="period">.</span></span></h1><p>Control autonomous payment actions with explicit intent, deterministic policies and traceable decisions.</p></div><div className="hero-field"><SecurityCore /><span className="field-caption">LIVE SECURITY FIELD / 001</span></div><div className="hero-footer"><div><span className="eyebrow">DETERMINISTIC POLICY ENGINE</span><strong><span className="status-dot" /> ONLINE</strong></div><div className="threat-count"><strong>14</strong><span>THREATS<br />BLOCKED</span></div><button className="text-button" onClick={enterControl}>ENTER CONTROL <ArrowRight size={16} /></button></div><a href="#guardrails" className="scroll-cue"><ArrowDown size={14} /> SCROLL TO OPERATE</a></section>
      <section id="guardrails" className="story-section problem-section section-frame"><div className="section-index">02 / THE PROBLEM</div><div className="story-heading"><span className="eyebrow">AUTONOMOUS ACTION / UNBOUNDED RISK</span><h2>AGENTS NEED<br /><em>GUARDRAILS.</em></h2></div><div className="guardrail-field"><div className="agent-word">AGENT</div>{["IDENTITY", "BUDGET", "CATEGORY", "VELOCITY", "TIME"].map((item, i) => <span className={`constraint constraint--${i + 1}`} key={item}>{item}</span>)}<div className="guardrail-ring" /></div><p className="section-note">An agent can act in milliseconds. A contract gives every action a boundary before it reaches the payment rail.</p></section>
      <section id="policies" className="story-section contract-section section-frame"><div className="section-index">03 / INTENT CONTRACT</div><div className="story-heading"><span className="eyebrow">PARSE / STRUCTURE / ENFORCE</span><h2>HUMAN INTENT<br /><em>BECOMES POLICY.</em></h2></div><div className="contract-grid"><div className="quote-panel"><span className="eyebrow">HUMAN INTENT</span><blockquote>"Book a flight to Mumbai for under INR 10,000."</blockquote><span className="parse-arrow">↓ PARSE</span></div><div className="contract-panel"><span className="eyebrow">INTENT CONTRACT / ACTIVE</span>{[["max_amount", "INR 10,000"], ["category", "travel"], ["velocity", "2 / hour"], ["time_window", "today"]].map(([key, value]) => <div className="contract-row" key={key}><span>{key}</span><strong>{value}</strong></div>)}<div className="policy-gate"><ShieldCheck size={15} /> DETERMINISTIC POLICY GATE</div></div></div></section>
      <section id="demo" className="story-section guard-section section-frame"><div className="section-index">04 / THE GUARD</div><div className="story-heading"><span className="eyebrow">REQUEST INTERCEPTION / ZERO GUESSWORK</span><h2>THE REQUEST<br /><em>MEETS THE BOUNDARY.</em></h2></div><div className="guard-demo"><div className="guard-demo__agent">AGENT<br /><small>authenticated</small></div><div className="guard-demo__boundary"><div className="guard-demo__core">POLICY<br />CORE</div><span className="guard-pulse guard-pulse--one" /><span className="guard-pulse guard-pulse--two" /></div><div className="guard-demo__request">TOOL.PAYMENT()<br /><small>INR 12,500 / travel</small></div></div><div className="guard-legend"><span><i className="legend-dot legend-dot--green" /> CONTRACT ALIGNED / PASS</span><span><i className="legend-dot legend-dot--red" /> POLICY VIOLATION / BLOCK</span></div></section>
      <section id="threats" className="story-section incident-section section-frame"><div className="section-index">05 / INCIDENT REPLAY</div><div className="story-heading"><span className="eyebrow">REPLAY / CATEGORY DRIFT / 001</span><h2>WATCH AN ATTACK<br /><em>GET STOPPED.</em></h2></div><div className="incident-grid"><div className="incident-copy"><div className="incident-alert"><span className="status-dot status-dot--red" /> INCIDENT DETECTED <strong>BLOCKED</strong></div><p>An authenticated agent attempted to move outside its grocery contract. The policy gate closed the path and recorded the decision.</p><button className="text-button" onClick={() => setIncidentStep(5)}>REPLAY EVENT <ArrowRight size={16} /></button></div><div className="event-stream" aria-label="Incident event replay">{incident.map(([time, event, tone], index) => <div className={`event-row event-row--${tone} ${index <= incidentStep ? "event-row--visible" : ""}`} key={`${time}-${event}`}><time>{time}</time><span>{event}</span>{index === 6 && <strong>BLOCKED</strong>}</div>)}</div></div></section>
      <section id="architecture" className="story-section architecture-section section-frame"><div className="section-index">06 / ARCHITECTURE</div><div className="story-heading"><span className="eyebrow">DECISION LINEAGE / EVERY ACTION</span><h2>EVERY ACTION<br /><em>LEAVES A TRAIL.</em></h2></div><div className="architecture-line">{stages.map((stage, index) => <div className="architecture-stage" key={stage}><span>0{index + 1}</span><strong>{stage}</strong><p>{["Verify the caller.", "Translate human intent.", "Evaluate hard limits.", "Control payment tools.", "Escalate ambiguity.", "Record the lineage."][index]}</p>{index < stages.length - 1 && <ArrowRight className="architecture-arrow" size={18} />}</div>)}</div></section>
      <section className="control-preview section-frame"><div><span className="eyebrow">07 / LIVE CONTROL PLANE</span><h2>THE GUARD DOES<br /><em>NOT GUESS.</em></h2><p>See decisions, incidents and audit trails in the operational control plane.</p></div><button className="text-button text-button--large" onClick={enterControl}>INITIALIZE SANDBOX <ArrowRight size={18} /></button></section>
    </main>
    <footer className="experience-footer section-frame"><div className="wordmark">AGENT<span>GUARD</span><sup>®</sup></div><span className="eyebrow"><span className="status-dot" /> ALL SYSTEMS OPERATIONAL</span><span className="footer-meta">POLICY ENGINE / 2026<br />RAZORPAY INTEGRATION</span></footer>
  </div>;
}
