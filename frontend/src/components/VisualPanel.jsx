import React, { useState, useEffect } from 'react';
import katex from 'katex';
import { 
  Activity, 
  Cpu, 
  Sliders, 
  Waves, 
  Layers, 
  Code2, 
  LineChart, 
  CheckCircle2,
  Sparkles,
  Calculator
} from 'lucide-react';
import GraphVisual from './GraphVisual';

export default function VisualPanel({ visualInstruction }) {
  const [sliderR, setSliderR] = useState(4);
  const [sliderV, setSliderV] = useState(12);

  // Sync initial parameters
  useEffect(() => {
    if (visualInstruction?.data?.resistance) {
      setSliderR(visualInstruction.data.resistance);
    }
    if (visualInstruction?.data?.voltage) {
      setSliderV(visualInstruction.data.voltage);
    }
  }, [visualInstruction]);

  // KaTeX helper
  const renderMath = (latex) => {
    try {
      return { __html: katex.renderToString(latex, { throwOnError: false }) };
    } catch {
      return { __html: latex };
    }
  };

  if (!visualInstruction) {
    return (
      <div className="glass-panel whiteboard-surface" style={{ height: '340px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Whiteboard ready for concept presentation.</p>
      </div>
    );
  }

  const { type = 'circuit', title, caption, data } = visualInstruction;

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', height: '100%', gap: '12px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '6px', borderRadius: '8px', background: '#EFF6FF', color: '#2563EB' }}>
            <Activity size={18} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0F172A' }}>{title}</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{caption}</span>
          </div>
        </div>
        <span className="badge badge-indigo">{type.replace(/_/g, ' ')}</span>
      </div>

      {/* Main Canvas Area */}
      <div className="whiteboard-surface" style={{ 
        flex: 1, 
        minHeight: '300px', 
        padding: '20px', 
        position: 'relative', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center', 
        alignItems: 'center' 
      }}>

        {/* 1. SCENE TYPE: CIRCUIT SIMULATION */}
        {type === 'circuit' && (
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '14px' }}>
            {(() => {
              const current = (sliderV / Math.max(0.1, sliderR)).toFixed(2);
              const electronDuration = Math.max(0.4, Math.min(3.5, 3.0 / Math.max(0.2, current)));

              return (
                <>
                  {/* Circuit SVG Diagram */}
                  <svg viewBox="0 0 460 200" style={{ width: '100%', maxWidth: '440px', height: '180px' }}>
                    {/* Wire Loop */}
                    <rect x="50" y="25" width="360" height="150" rx="14" fill="none" stroke="#334155" strokeWidth="4" />
                    
                    {/* Flowing Electrons */}
                    <rect 
                      x="50" y="25" width="360" height="150" rx="14" 
                      fill="none" 
                      stroke="#06B6D4" 
                      strokeWidth="3" 
                      className="electron-path"
                      style={{ animationDuration: `${electronDuration}s` }}
                    />

                    {/* DC Voltage Source (Left) */}
                    <g transform="translate(50, 100)">
                      <rect x="-18" y="-24" width="36" height="48" rx="6" fill="#1E293B" stroke="#6366F1" strokeWidth="2" />
                      <line x1="-12" y1="-8" x2="12" y2="-8" stroke="#F8FAFC" strokeWidth="3" />
                      <line x1="-6" y1="8" x2="6" y2="8" stroke="#94A3B8" strokeWidth="2" />
                      <text x="-36" y="5" fill="#A5B4FC" fontSize="12" fontWeight="700">+{sliderV}V</text>
                      <text x="24" y="5" fill="#64748B" fontSize="11">Source</text>
                    </g>

                    {/* Variable Resistor (Top) */}
                    <g transform="translate(230, 25)">
                      <rect x="-42" y="-16" width="84" height="32" rx="4" fill="#1E293B" stroke="#F59E0B" strokeWidth="2" />
                      <path d="M -30 0 L -20 -8 L -10 8 L 0 -8 L 10 8 L 20 -8 L 30 0" fill="none" stroke="#F59E0B" strokeWidth="2" />
                      <text x="0" y="-20" textAnchor="middle" fill="#FCD34D" fontSize="12" fontWeight="700">
                        R = {sliderR} Ω
                      </text>
                    </g>

                    {/* Ammeter (Right) */}
                    <g transform="translate(410, 100)">
                      <circle cx="0" cy="0" r="22" fill="#1E293B" stroke="#10B981" strokeWidth="2" />
                      <text x="0" y="4" textAnchor="middle" fill="#6EE7B7" fontSize="12" fontWeight="800">A</text>
                      <text x="28" y="5" fill="#6EE7B7" fontSize="13" fontWeight="700">
                        {current} A
                      </text>
                    </g>

                    {/* Formula Box in Center */}
                    <g transform="translate(230, 105)">
                      <rect x="-90" y="-18" width="180" height="36" rx="8" fill="rgba(15, 23, 42, 0.95)" stroke="rgba(255,255,255,0.12)" />
                      <text x="0" y="5" textAnchor="middle" fill="#F8FAFC" fontSize="13" fontWeight="600" fontFamily="var(--font-mono)">
                        I = V / R = {sliderV} / {sliderR} = {current}A
                      </text>
                    </g>
                  </svg>

                  {/* Interactive Slider */}
                  <div style={{ width: '100%', maxWidth: '440px', background: 'rgba(255,255,255,0.04)', padding: '12px 16px', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <span style={{ color: '#FCD34D', fontWeight: 600 }}>Adjust Resistance (R):</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{sliderR} Ohms</span>
                    </div>
                    <input 
                      type="range" 
                      min="1" 
                      max="20" 
                      step="1" 
                      value={sliderR} 
                      onChange={(e) => setSliderR(Number(e.target.value))}
                      style={{ width: '100%', accentColor: '#F59E0B', cursor: 'pointer' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>1Ω (High Flow: {sliderV}A)</span>
                      <span>20Ω (Low Flow: {(sliderV/20).toFixed(2)}A)</span>
                    </div>
                  </div>

                  {/* Water Pipe Hydraulic Analogy Card if present */}
                  {data?.analogy && (
                    <div style={{ width: '100%', maxWidth: '440px', background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.25)', borderRadius: '10px', padding: '10px 14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Waves size={20} color="#06B6D4" />
                      <div style={{ fontSize: '0.8rem', color: '#E0F2FE' }}>
                        <strong>Hydraulic Analogy:</strong> {data.analogy}
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        )}

        {/* 2. SCENE TYPE: EQUATION / MATH DERIVATION */}
        {(type === 'equation' || type === 'math_derivation') && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '440px' }}>
            {data?.steps?.map((step, idx) => (
              <div 
                key={idx} 
                style={{
                  background: idx === (data.active_step ?? 0) ? 'rgba(99, 102, 241, 0.16)' : 'rgba(255, 255, 255, 0.03)',
                  border: idx === (data.active_step ?? 0) ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontSize: '1.25rem', marginBottom: '4px' }} dangerouslySetInnerHTML={renderMath(step.latex)} />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{step.explanation}</span>
                </div>
                {idx === (data.active_step ?? 0) && <span className="badge badge-indigo">Active Focus</span>}
              </div>
            ))}
          </div>
        )}

        {/* 3. SCENE TYPE: GRAPH */}
        {type === 'graph' && (
          <GraphVisual title={title} fixedV={data?.voltage || 12} />
        )}

        {/* 4. SCENE TYPE: CODE TRACE */}
        {(type === 'code' || type === 'code_trace') && (
          <div style={{ width: '100%', maxWidth: '460px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#38BDF8', fontSize: '0.8rem', fontWeight: 600 }}>
              <Code2 size={16} />
              <span>Language: {data?.language || 'Python'}</span>
            </div>
            <pre style={{ background: '#090D16', padding: '14px', borderRadius: '8px', fontSize: '0.85rem', color: '#38BDF8', overflowX: 'auto', border: '1px solid rgba(255,255,255,0.08)' }}>
              <code>{data?.code}</code>
            </pre>
            {data?.trace_state && (
              <div style={{ display: 'flex', gap: '12px', background: 'rgba(255,255,255,0.04)', padding: '8px 14px', borderRadius: '8px', fontSize: '0.8rem' }}>
                {Object.entries(data.trace_state).map(([k, v]) => (
                  <span key={k}><strong>{k}:</strong> {String(v)}</span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 5. SCENE TYPE: CONCEPT MAP / DIAGRAM */}
        {(type === 'diagram' || type === 'concept_map') && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%', maxWidth: '420px' }}>
            {data?.concepts?.map((c, i) => (
              <div 
                key={i} 
                style={{
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: c === data.active_concept ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                  border: c === data.active_concept ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px'
                }}
              >
                <Layers size={16} color={c === data.active_concept ? '#818CF8' : '#94A3B8'} />
                <span style={{ fontSize: '0.88rem', fontWeight: c === data.active_concept ? 700 : 500 }}>{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* 6. SCENE TYPE: WORKED EXAMPLE */}
        {type === 'worked_example' && (
          <div style={{ width: '100%', maxWidth: '440px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', fontWeight: 700, fontSize: '0.9rem' }}>
              <Calculator size={18} />
              <span>Step-by-Step Worked Problem</span>
            </div>
            <p style={{ fontSize: '0.88rem', color: '#F8FAFC' }}>
              {data?.problem || "Given a 24V supply and 6Ω resistor, calculate current flow."}
            </p>
            <div style={{ background: '#0F172A', padding: '10px 14px', borderRadius: '8px', borderLeft: '3px solid #10B981', fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: '#6EE7B7' }}>
              {data?.solution || "Step 1: Formula I = V / R\nStep 2: Substitute: I = 24 / 6\nStep 3: Result = 4.0 Amperes"}
            </div>
          </div>
        )}

        {/* 7. SCENE TYPE: SUMMARY / CONCEPT CARD */}
        {(type === 'summary' || type === 'concept_card') && (
          <div style={{ width: '100%', maxWidth: '420px', background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '12px', padding: '18px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#A5B4FC', fontWeight: 700, fontSize: '0.95rem' }}>
              <Sparkles size={18} />
              <span>Key Concept Takeaway</span>
            </div>
            <p style={{ fontSize: '0.88rem', color: '#F1F5F9', lineHeight: 1.5 }}>
              {data?.takeaway || "Ohm's Law defines the relationship between potential difference and charge flow. For a constant voltage, current is inversely proportional to resistance."}
            </p>
          </div>
        )}

      </div>
    </div>
  );
}
