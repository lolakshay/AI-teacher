import React, { useState } from 'react';

export default function GraphVisual({ title = "V-I Characteristic Curve", fixedV = 12 }) {
  const [resistance, setResistance] = useState(4);

  // Generate coordinate points for V vs I (Ohmic straight line with slope R)
  // V = I * R => I = V / R
  const points = [];
  for (let v = 0; v <= 24; v += 2) {
    const i = v / resistance;
    // Map to SVG coordinates: width 360, height 180, margins x:40, y:20
    const x = 40 + (v / 24) * 280;
    const y = 160 - (i / 8) * 130;
    points.push(`${x},${y}`);
  }

  const currentAtFixed = (fixedV / resistance).toFixed(2);
  const fixedX = 40 + (fixedV / 24) * 280;
  const fixedY = 160 - (currentAtFixed / 8) * 130;

  return (
    <div style={{ width: '100%', maxWidth: '460px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <svg viewBox="0 0 360 190" style={{ width: '100%', height: '170px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
        {/* Grid lines */}
        {[40, 110, 180, 250, 320].map((x, idx) => (
          <line key={'vx' + idx} x1={x} y1="20" x2={x} y2="160" stroke="#1E293B" strokeWidth="1" strokeDasharray="3,3" />
        ))}
        {[30, 65, 95, 125, 160].map((y, idx) => (
          <line key={'hy' + idx} x1="40" y1={y} x2="320" y2={y} stroke="#1E293B" strokeWidth="1" strokeDasharray="3,3" />
        ))}

        {/* Axes */}
        <line x1="40" y1="160" x2="330" y2="160" stroke="#64748B" strokeWidth="2" />
        <line x1="40" y1="160" x2="40" y2="15" stroke="#64748B" strokeWidth="2" />

        {/* Axis Labels */}
        <text x="335" y="164" fill="#94A3B8" fontSize="11" fontWeight="600">V (Volts)</text>
        <text x="36" y="14" fill="#94A3B8" fontSize="11" fontWeight="600" textAnchor="end">I (Amps)</text>

        {/* V-I Curve Line */}
        <polyline
          fill="none"
          stroke="#06B6D4"
          strokeWidth="3"
          points={points.join(' ')}
        />

        {/* Fixed Operating Point Dot */}
        <circle cx={fixedX} cy={fixedY} r="5" fill="#F59E0B" stroke="#FFF" strokeWidth="1.5" />
        <text x={fixedX + 8} y={fixedY - 6} fill="#FCD34D" fontSize="11" fontWeight="700">
          ({fixedV}V, {currentAtFixed}A)
        </text>
      </svg>

      {/* Slider to alter slope R */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', background: 'rgba(255, 255, 255, 0.03)', padding: '10px 14px', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
          <span style={{ color: '#FCD34D', fontWeight: 600 }}>Slope / Resistance (R = ΔV/ΔI):</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{resistance} Ω</span>
        </div>
        <input 
          type="range"
          min="1"
          max="12"
          step="1"
          value={resistance}
          onChange={(e) => setResistance(Number(e.target.value))}
          style={{ width: '100%', accentColor: '#06B6D4', cursor: 'pointer' }}
        />
        <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
          Higher resistance produces a flatter slope (less current for the same voltage).
        </span>
      </div>
    </div>
  );
}
