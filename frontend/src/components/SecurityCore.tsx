import { useEffect, useRef, useState } from "react";
import { Activity, ArrowUpRight } from "lucide-react";

type SecurityCoreProps = {
  compact?: boolean;
};

const nodes = [
  { label: "IDENTITY", angle: -34, distance: 158, tone: "green" },
  { label: "TOOL CALL", angle: 48, distance: 190, tone: "red" },
  { label: "POLICY CHECK", angle: 138, distance: 170, tone: "amber" },
  { label: "AUDIT EVENT", angle: 224, distance: 185, tone: "green" },
];

export default function SecurityCore({ compact = false }: SecurityCoreProps) {
  const fieldRef = useRef<HTMLDivElement>(null);
  const [activeNode, setActiveNode] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setActiveNode((current) => (current + 1) % nodes.length), 2400);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const field = fieldRef.current;
    if (!field || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const onMove = (event: PointerEvent) => {
      const bounds = field.getBoundingClientRect();
      const x = (event.clientX - bounds.left) / bounds.width - 0.5;
      const y = (event.clientY - bounds.top) / bounds.height - 0.5;
      field.style.setProperty("--field-x", `${x * 16}px`);
      field.style.setProperty("--field-y", `${y * 16}px`);
    };
    field.addEventListener("pointermove", onMove);
    return () => field.removeEventListener("pointermove", onMove);
  }, []);

  return (
    <div ref={fieldRef} className={`security-core ${compact ? "security-core--compact" : ""}`} aria-label="Animated security field showing requests passing through a policy boundary">
      <div className="security-core__noise" />
      <div className="security-core__orbit security-core__orbit--outer" />
      <div className="security-core__orbit security-core__orbit--mid" />
      <div className="security-core__orbit security-core__orbit--inner" />
      <div className="security-core__boundary" />
      <div className="security-core__crosshair security-core__crosshair--horizontal" />
      <div className="security-core__crosshair security-core__crosshair--vertical" />
      <div className="security-core__core">
        <div className="security-core__core-mark">AG</div>
        <span>POLICY<br />ENGINE</span>
      </div>
      {nodes.map((node, index) => (
        <div
          key={node.label}
          className={`security-node security-node--${node.tone} ${activeNode === index ? "security-node--active" : ""}`}
          style={{ "--node-angle": `${node.angle}deg`, "--node-distance": `${node.distance}px` } as React.CSSProperties}
        >
          <span className="security-node__dot" />
          <span className="security-node__label">{node.label}</span>
        </div>
      ))}
      <div className="security-core__telemetry"><Activity size={12} /> REQUEST STREAM / {String(activeNode + 1).padStart(2, "0")} ACTIVE</div>
      <div className="security-core__status"><span /> FIELD STABLE <ArrowUpRight size={13} /></div>
    </div>
  );
}
